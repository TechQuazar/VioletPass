import psycopg2
import os
import json
import redis
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

def decimal_to_str(value):
    """Convert Decimal to string for JSON serialization."""
    if isinstance(value, Decimal):
        return str(value)
    return value

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

def lambda_handler(event, context):
    print('Received Event:', event)
    http_method = event.get("httpMethod", "").upper()

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        query_params = event.get("queryStringParameters", {})
        event_id = query_params.get("event_id")
        ticket_query = """
                    SELECT seat_no, category, cost, status
                    FROM tickets
                    WHERE event_id = %s;
                """
        cur.execute(ticket_query, (event_id,))
        seats = cur.fetchall()
        # Process seats and verify locks with Redis
        all_seats = []
        for row in seats:
            seat_no, category, cost, status = row
            lock_key = f"{event_id}:{seat_no}"  # Redis lock key format

            # Cross-check with Redis to update the status if locked
            if redis_client.get(lock_key):
                status = "locked"  # Update status if the seat is locked

            all_seats.append({
                "seat_no": seat_no,
                "category": category,
                "cost": decimal_to_str(cost),  # Convert Decimal to string
                "status": status  # Include the updated status
            })
        
        return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps(all_seats)
            }


    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({"error": str(e)})
        }


