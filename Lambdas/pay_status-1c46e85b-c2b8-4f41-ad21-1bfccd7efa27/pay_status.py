import json
import psycopg2
import os
import time
from datetime import datetime, timedelta

# PostgreSQL connection parameters
DB_PARAMS = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
}

def check_payment_status(payment_id):
    """Check payment status in PostgreSQL."""
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT status
            FROM bookings
            WHERE payment_id = %s
        """, (payment_id,))
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        cur.close()
        conn.close()

def lambda_handler(event, context):
    try:
        # Extract payment_id from query parameters
        payment_id = event['queryStringParameters']['payment_id']
        
        # Set timeout duration and calculate end time
        timeout_seconds = 25
        end_time = datetime.now() + timedelta(seconds=timeout_seconds)
        
        # Keep checking until timeout
        while datetime.now() < end_time:
            payment_status = check_payment_status(payment_id)
            print('payment_status',payment_status)
            
            if payment_status is not None:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',  # Allow all origins
                        'Access-Control-Allow-Methods': 'GET',  # Allow only GET method
                        'Access-Control-Allow-Headers': 'Content-Type'  # Allow specific headers
                    },
                    'body': json.dumps({'status': payment_status})
                }
            
            time.sleep(0.5)  # Check every 500ms
        
        # If we reach here, timeout occurred
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'status': 'FAILURE'})
        }
            
    except Exception as e:
        print(f"Error checking payment status: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'status': 'FAILURE', 'error': str(e)})
        }
