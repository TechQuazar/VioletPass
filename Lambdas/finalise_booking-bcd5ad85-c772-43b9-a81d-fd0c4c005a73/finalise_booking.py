import json
import redis
import psycopg2
import os
import boto3
from psycopg2.extras import execute_values
from datetime import datetime

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

# SES client
# ses_client = boto3.client('ses', region_name='us-east-1')
SENDER_EMAIL = 'sidharthareddy02@gmail.com'

def lambda_handler(event, context):
    """Handle SQS messages and finalize bookings."""
    responses = []

    print("Lambda handler invoked.")
    print(f"Event received: {json.dumps(event)}")

    for record in event.get("Records", []):
        try:
            print(f"Processing record: {record}")
            # Parse the SQS message body
            message_body = json.loads(record["body"])

            # Extract fields
            event_id = message_body.get("event_id")
            user_id = message_body.get("user_id")
            seat_nos = message_body.get("seat_numbers")
            payment_id = message_body.get("payment_id")
            reference_id = message_body.get("reserve_id")
            card_number = message_body.get("card_number")
            email_id = message_body.get("email_id")

            print(f"Parsed message: user_id={user_id}, seat_nos={seat_nos}, payment_id={payment_id}, reference_id={reference_id}, card_number={card_number}, email_id={email_id}")

            # Validate card number length
            if len(card_number) != 16:
                print(f"Card number validation failed for message ID {record.get('messageId')}. Writing FAILURE to database.")
                write_failure_to_db(payment_id, reference_id, user_id, event_id, seat_nos, "Invalid card number")
                # send_email(email_id, "Booking Failure", f"Your booking failed due to invalid card number. Seat numbers: {seat_nos}")
                responses.append({"messageId": record.get("messageId"), "status": "failure", "error": "Invalid card number"})
                continue

            # Validate required fields
            if not all([event_id, user_id, seat_nos, payment_id, reference_id, email_id]):
                raise ValueError("Invalid message: Missing required fields (event_id, user_id, seat_numbers, payment_id, reference_id, email_id)")

            # Finalize booking
            response = finalize_booking(event_id, user_id, seat_nos, payment_id, reference_id)
            print(f"Booking successful for message ID {record.get('messageId')}: {response}")

            # Send success email
            # send_email(email_id, "Booking Confirmation", f"Your booking was successful! Seat numbers: {seat_nos}")
            responses.append({"messageId": record.get("messageId"), "status": "success", "response": response})

        except Exception as e:
            print(f"Error processing record with message ID {record.get('messageId')}: {str(e)}")
            responses.append({"messageId": record.get("messageId"), "status": "failure", "error": str(e)})

    print(f"Lambda handler completed. Responses: {responses}")
    return {"responses": responses}

def send_email(recipient, subject, body):
    """Send an email using AWS SES."""
    try:
        print(f"Sending email to {recipient} with subject: {subject}")
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print(f"Email sent successfully! MessageId: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

def write_failure_to_db(payment_id, reference_id, user_id, event_id, seat_nos, error_message):
    """Write a failure record directly to the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO bookings 
            (payment_id, reference_id, status, user_id, event_id, seat_numbers, error_message,booking_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (payment_id, reference_id, 'failure', user_id, event_id, seat_nos, error_message,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )

        print(f"Failure record written to database for payment_id={payment_id}, reference_id={reference_id}")

    except Exception as e:
        print(f"Error writing failure to database: {str(e)}")
        raise e

    finally:
        conn.close()
        print("Database connection closed.")

def finalize_booking(event_id, user_id, seat_nos, payment_id, reference_id):
    """Finalize booking using Redis locks and PostgreSQL row-level locking."""
    print(f"Starting finalize_booking: user_id={user_id}, seat_nos={seat_nos}")

    # First verify all locks before establishing any database connections
    for seat_no in seat_nos:
        lock_key = f"{event_id}:{seat_no}"
        locked_by = redis_client.get(lock_key)
        if locked_by != user_id:
            print(f"Seat {seat_no} is not locked by user {user_id}. Locked by: {locked_by}")
            raise Exception(f"Seat {seat_no} is not locked by user {user_id}.")

    # Only proceed with database operations if all locks are verified
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        conn.autocommit = False
        cur = conn.cursor()

        seat_tuple = tuple(seat_nos)

        # Lock tickets rows
        cur.execute(
            """
            SELECT seat_no, status
            FROM tickets
            WHERE event_id = %s AND seat_no = ANY(%s)
            FOR UPDATE
            """,
            (event_id, list(seat_tuple))
        )
        rows = cur.fetchall()
        print(f"Rows locked: {rows}")

        if len(rows) != len(seat_nos):
            raise Exception("Some requested seats do not exist.")

        # Check that all are available
        unavailable = [r[0] for r in rows if r[1] != 'available']
        if unavailable:
            print(f"Seats unavailable: {unavailable}")
            raise Exception(f"Seats {unavailable} are not available.")

        # Lock the event row to ensure consistent decrement of available_tickets
        cur.execute(
            """
            SELECT available_tickets
            FROM events
            WHERE event_id = %s
            FOR UPDATE
            """,
            (event_id,)
        )
        event_row = cur.fetchone()
        if not event_row:
            raise Exception("Event not found.")
        current_available = event_row[0]

        print(f"Current available tickets: {current_available}")

        # Check if enough tickets are available
        needed = len(seat_nos)
        if current_available < needed:
            raise Exception("Not enough available tickets for this event.")

        # Update tickets to 'booked' in bulk
        cur.execute(
            """
            UPDATE tickets
            SET status = 'booked'
            WHERE event_id = %s AND seat_no = ANY(%s) AND status = 'available'
            RETURNING seat_no
            """,
            (event_id, list(seat_tuple))
        )
        updated_seats = cur.fetchall()
        print(f"Seats updated to 'booked': {updated_seats}")

        if len(updated_seats) != needed:
            raise Exception("Not all seats could be booked. Possibly concurrent modification.")

        # Insert into bookings table
        cur.execute(
            """
            INSERT INTO bookings 
            (payment_id, reference_id, status, user_id, event_id, seat_numbers,booking_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING booking_id
            """,
            (payment_id, reference_id, 'success', user_id, event_id, seat_nos,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        booking_id = cur.fetchone()[0]

        # Decrement available tickets safely
        cur.execute(
            """
            UPDATE events
            SET available_tickets = available_tickets - %s
            WHERE event_id = %s AND available_tickets >= %s
            """,
            (needed, event_id, needed)
        )
        if cur.rowcount == 0:
            raise Exception("Not enough available tickets after re-checking the event.")

        # Commit transaction
        conn.commit()
        print("Transaction committed successfully.")

        # Clean up Redis after successful commit
        # Release seat locks
        for seat_no in seat_nos:
            redis_client.delete(f"{event_id}:{seat_no}")
        # Delete booking reservation
        redis_client.delete(f"booking:{reference_id}")
        print(f"Released Redis locks and cleaned up reservation for reference_id: {reference_id}")

        return {
            "success": True, 
            "booking_id": booking_id,
            "payment_id": payment_id,
            "reference_id": reference_id,
            "status": "success",
            "user_id": user_id,
            "seat_numbers": seat_nos
        }

    except Exception as e:
        conn.rollback()
        print(f"Transaction rolled back due to error: {str(e)}")
        # Only release locks if we got past the initial lock verification
        if "is not locked by user" not in str(e):
            for seat_no in seat_nos:
                redis_client.delete(f"{event_id}:{seat_no}")
            print(f"Released Redis locks due to database error for seats: {seat_nos}")
        raise e

    finally:
        conn.close()
        print("Database connection closed.")
