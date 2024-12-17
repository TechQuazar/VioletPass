import json
import redis
import psycopg2
import os
import uuid
from datetime import datetime
from psycopg2.extras import execute_values

# Redis connection
redis_client = redis.StrictRedis(
    host=os.environ["REDIS_HOST"],
    port=6379,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    ssl=True,
    retry_on_timeout=True
)

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
}

LOCK_TTL = 600  # 10 minutes
LOCK_TTL_FAIL = 120 #2 minutes

def lambda_handler(event, context):
    """Reserve tickets using Redis locks, process multiple SQS messages, and store booking IDs in Redis."""
    responses = []
    print("Received event: ", event)

    for record in event.get("Records", []):
        try:
            # Parse the SQS message body
            message_body = json.loads(record["body"])
            print(f"Processing record {record['messageId']}")
            print("Parsed message body: ", message_body)

            event_id = message_body["event_id"]
            user_id = message_body["user_id"]
            seat_nos = message_body["seat_numbers"]
            reserve_id = message_body['reserve_id']

            print(f"Event ID: {event_id}, User ID: {user_id}, Seats: {seat_nos}")

            reserved_seats = []
            failed_seats = []

            # Generate a unique reserve ID
            # reserve_id = str(uuid.uuid4())
            # print(f"Generated reserve ID: {reserve_id}")

            # PostgreSQL connection
            conn = psycopg2.connect(**DB_PARAMS)
            cur = conn.cursor()

            try:
                print("Attempting to lock seats in Redis...")
                # Attempt to lock all seats in Redis
                for seat_no in seat_nos:
                    lock_key = f"{event_id}:{seat_no}"
                    # Try to acquire lock
                    if redis_client.set(lock_key, user_id, nx=True, ex=LOCK_TTL):
                        reserved_seats.append(seat_no)
                        print(f"Locked seat {seat_no}")
                    else:
                        failed_seats.append({"seat_no": seat_no, "reason": "Already locked by another user"})
                        print(f"Failed to lock seat {seat_no}, already locked by another user")
                        break

                if failed_seats:
                    print("Failed to lock all seats, releasing acquired locks...")
                    # Release any acquired locks if not all were locked
                    for seat_no in reserved_seats:
                        redis_client.delete(f"{event_id}:{seat_no}")
                    redis_client.set(f"booking:{reserve_id}", "FAILED", ex=LOCK_TTL_FAIL)
                    response = {
                        "messageId": record["messageId"],
                        "success": False, 
                        "error": "Failed to reserve all seats", 
                        "failed_seats": failed_seats
                    }
                    responses.append(response)
                    continue  # Process next record

                print("Checking seat availability in PostgreSQL...")
                # Check availability in bulk
                seat_tuple = tuple(seat_nos)
                cur.execute("""
                    SELECT seat_no, status
                    FROM tickets
                    WHERE event_id = %s AND seat_no = ANY(%s)
                """, (event_id, list(seat_tuple)))
                rows = cur.fetchall()

                print("Query result: ", rows)
                # First check if all requested seats exist
                if len(rows) != len(seat_nos):
                    # Find which seats don't exist
                    found_seats = {row[0] for row in rows}
                    missing_seats = [seat for seat in seat_nos if seat not in found_seats]
                    print(f"Some seats do not exist: {missing_seats}")
                    # Release locks for all seats
                    for seat_no in seat_nos:
                        redis_client.delete(f"{event_id}:{seat_no}")
                    response = {
                        "messageId": record["messageId"],
                        "success": False,
                        "error": "Some seats do not exist",
                        "failed_seats": [{"seat_no": s, "reason": "Seat does not exist"} for s in missing_seats]
                    }
                    redis_client.set(f"booking:{reserve_id}", "FAILED", ex=LOCK_TTL_FAIL)
                    responses.append(response)
                    continue  # Process next record


                # Verify all are available
                not_available = [r[0] for r in rows if r[1] != 'available']
                if not_available:
                    print("Some seats are not available, releasing locks...")
                    # Release locks for these seats
                    for seat_no in seat_nos:
                        redis_client.delete(f"{event_id}:{seat_no}")
                    response = {
                        "messageId": record["messageId"],
                        "success": False,
                        "error": "Some seats are not available",
                        "failed_seats": [{"seat_no": s, "reason": "Not available"} for s in not_available]
                    }
                    redis_client.set(f"booking:{reserve_id}", "FAILED", ex=LOCK_TTL_FAIL)
                    responses.append(response)
                    continue  # Process next record

                print("All seats are available, storing reservation in Redis...")
                # Store the reservation in Redis
                booking_data = {
                    "eventId": event_id,
                    "userId": user_id,
                    "seats": seat_nos,
                }
                redis_client.set(f"booking:{reserve_id}", "SUCCESS", ex=LOCK_TTL)
                print("Reservation stored successfully in Redis")

                response = {
                    "messageId": record["messageId"],
                    "success": True,
                    "reserved_seats": seat_nos,
                    "reserveId": reserve_id
                }
                responses.append(response)

            except Exception as e:
                print("Error during reservation process, releasing locks...")
                # On any error, release locks
                for seat_no in seat_nos:
                    redis_client.delete(f"{event_id}:{seat_no}")
                redis_client.set(f"booking:{reserve_id}", "FAILED", ex=LOCK_TTL_FAIL)
                print(f"Error: {str(e)}")
                responses.append({
                    "messageId": record["messageId"],
                    "success": False,
                    "error": str(e)
                })
            finally:
                print("Closing database connection...")
                cur.close()
                conn.close()

        except Exception as e:
            print(f"Unexpected error processing record {record.get('messageId')}: {str(e)}")
            responses.append({
                "messageId": record.get('messageId'),
                "success": False,
                "error": str(e)
            })

    print("Completed processing all records")
    print(f"Responses: {responses}")
    return {"batchResults": responses}