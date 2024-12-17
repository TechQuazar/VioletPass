import json
import psycopg2
import os

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
}

def lambda_handler(event, context):
    """Handle POST requests to cancel grouped bookings and release all seats in the booking."""
    print(event)
    try:
        # Parse the request body from the API Gateway event
        body = event
        user_id = body.get('user_id')
        event_id = body.get('event_id')
        booking_id = body.get('payment_id')  # Booking ID to identify a grouped booking

        if not user_id or not event_id or not booking_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required parameters"})
            }

        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        try:
            # Verify that the booking exists and belongs to the user
            cur.execute("""
                SELECT seat_numbers, status
                FROM bookings
                WHERE event_id = %s AND user_id = %s AND payment_id = %s
            """, (event_id, user_id, booking_id))

            booking = cur.fetchone()
            print("Booking fetched:", booking)

            if not booking:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Booking not found or does not belong to the user"})
                }

            seat_numbers = booking[0]  # The list of seats in the booking
            booking_status = booking[1]

            if booking_status != 'success':
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Cannot cancel a booking that is not active"})
                }

            # Ensure seat_numbers is a list (if stored as JSON in the database)
            if not isinstance(seat_numbers, list):
                seat_numbers = json.loads(seat_numbers)

            print("Reverting seats:", seat_numbers)

            # Update the tickets table to make all seats in the group available
            cur.execute("""
                UPDATE tickets
                SET status = 'available'
                WHERE event_id = %s AND seat_no = ANY(%s)
            """, (event_id, seat_numbers))

            # Update the bookings table to set the booking status to FAILURE
            cur.execute("""
                UPDATE bookings
                SET status = 'failure'
                WHERE event_id = %s AND user_id = %s AND payment_id = %s
            """, (event_id, user_id, booking_id))

            # Increase available tickets for the event by the total number of seats in the booking
            released_tickets = len(seat_numbers)
            cur.execute("""
                UPDATE events
                SET available_tickets = available_tickets + %s
                WHERE event_id = %s
            """, (released_tickets, event_id))

            conn.commit()

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Booking cancelled successfully, and all seats in the booking released",
                    "released_seats": seat_numbers
                })
            }

        except Exception as e:
            print(f"Error while processing request: {str(e)}")
            conn.rollback()
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to cancel booking and release seats", "details": str(e)})
            }
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
