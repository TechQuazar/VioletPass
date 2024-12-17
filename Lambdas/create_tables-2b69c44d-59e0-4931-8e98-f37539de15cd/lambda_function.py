import json
import psycopg2
import os

def validate_and_update_seats(event, context=None):
    """Validate and update scanned seats in the bookings table."""
    DB_PARAMS = {
        'dbname': os.environ.get('DB_NAME', 'your_db_name'),
        'user': os.environ.get('DB_USER', 'your_db_user'),
        'password': os.environ.get('DB_PASSWORD', 'your_db_password'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    print('event',event)

    try:
        # # Use event directly if running in Lambda, else read from event.json
        # if isinstance(event, str):  # Simulate local testing
        #     with open(event, 'r') as f:
        #         event = json.load(f)

        # Parse input from event
        # body = json.loads(event['body'])
        # payment_id = body.get('payment_id')
        # seat_no = body.get('seat_no')
        query_params = event.get('queryStringParameters', {})
        payment_id = query_params.get('payment_id')
        seat_no = query_params.get('seat_no')
        print('QEu',query_params)

        if not payment_id or not seat_no:
            return {
                'statusCode': 400,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
                'body': json.dumps('Missing payment_id or seat_no')
            }

        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Fetch booking details using payment_id
        cur.execute("""
            SELECT scanned_seats, seat_numbers
            FROM bookings
            WHERE payment_id = %s;
        """, (payment_id,))
        result = cur.fetchone()

        if not result:
            return {
                'statusCode': 404,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
                'body': json.dumps('Booking not found')
            }
        print(result)
        scanned_seats, all_seats = result

        # Ensure all_seats is parsed as an array
        if not isinstance(all_seats, list):
            all_seats = all_seats.split(',')

        # Check if the seat has already been scanned
        if seat_no in scanned_seats:
            return {
                'statusCode': 409,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
                'body': json.dumps('Seat has already been scanned')
            }

        # Check if all seats have already been verified
        if len(scanned_seats) >= len(all_seats):
            return {
                'statusCode': 409,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
                'body': json.dumps('All seats have already been verified')
            }

        # Update the scanned_seats column
        cur.execute("""
            UPDATE bookings
            SET scanned_seats = array_append(scanned_seats, %s)
            WHERE payment_id = %s;
        """, (seat_no, payment_id))
        conn.commit()

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
            'body': json.dumps('Seat verified successfully')
        }

    except psycopg2.Error as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
            'body': json.dumps(f'Database error: {str(e)}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
                    },
            'body': json.dumps(f'Error: {str(e)}')
        }
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Local testing
if __name__ == "__main__":
    response = validate_and_update_seats("event.json")
    print(json.dumps(response, indent=2))
