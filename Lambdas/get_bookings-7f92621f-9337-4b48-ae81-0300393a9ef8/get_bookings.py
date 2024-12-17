import json
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from datetime import datetime

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
}

def lambda_handler(event, context):
    """Handle GET request to retrieve user bookings."""
    print(f"Received event: {json.dumps(event)}")

    # Extract user_id from query string parameters
    user_id = event.get("queryStringParameters", {}).get("user_id")
    if not user_id:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET"
            },
            "body": json.dumps({"error": "Missing user_id in request"})
        }

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Query bookings table for successful bookings by user_id
        cur.execute("""
            SELECT event_id, seat_numbers, payment_id, booking_time
            FROM bookings
            WHERE user_id = %s AND status = 'success'
        """, (user_id,))
        bookings = cur.fetchall()

        if not bookings:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET"
                },
                "body": json.dumps({"error": "No bookings found for the user"})
            }

        # Validate seat statuses in tickets table and fetch event details
        results = []
        for booking in bookings:
            event_id = booking["event_id"]
            seat_numbers = booking["seat_numbers"]
            payment_id = booking['payment_id']
            booking_time = booking['booking_time']

            # Query tickets table to validate seat statuses
            cur.execute("""
                SELECT seat_no, status
                FROM tickets
                WHERE event_id = %s AND seat_no = ANY(%s)
            """, (event_id, list(seat_numbers)))
            seat_statuses = cur.fetchall()

            # Filter only booked seats
            booked_seats = [seat["seat_no"] for seat in seat_statuses if seat["status"] == "booked"]

            # Query events table for additional event details
            cur.execute("""
                SELECT name, venue, location, start_date, end_date
                FROM events
                WHERE event_id = %s
            """, (event_id,))
            event_details = cur.fetchone()

            if not event_details:
                continue  # Skip if event details are missing

            results.append({
                "event_id": event_id,
                "booked_seats": booked_seats,
                "payment_id": payment_id,
                "booking_time": booking_time.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                "name": event_details["name"],
                "venue": event_details["venue"],
                "location": event_details["location"],
                "start_date": event_details["start_date"].strftime('%Y-%m-%d %H:%M:%S') if event_details["start_date"] else None,  # Convert datetime to string
                "end_date": event_details["end_date"].strftime('%Y-%m-%d %H:%M:%S') if event_details["end_date"] else None  # Convert datetime to string
            })

        # Close the connection
        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET"
            },
            "body": json.dumps({"user_id": user_id, "bookings": results})
        }

    except Exception as e:
        print(f"Error querying database: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET"
            },
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
