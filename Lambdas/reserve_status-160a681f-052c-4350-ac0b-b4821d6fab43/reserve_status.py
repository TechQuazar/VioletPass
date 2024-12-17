import json
import redis
import os
import time
from datetime import datetime, timedelta

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

def lambda_handler(event, context):
    print(event)
    try:
        # Extract reserve_id from API Gateway event
        reserve_id = event['queryStringParameters']['reserve_id']
        print(reserve_id)
        # Set timeout duration and calculate end time
        timeout_seconds = 25
        end_time = datetime.now() + timedelta(seconds=timeout_seconds)
        
        # Keep checking until timeout
        while datetime.now() < end_time:
            # Check Redis for booking status
            booking_status = redis_client.get(f"booking:{reserve_id}")
            print('Status',booking_status)
            if booking_status is not None:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',  # Allow all origins
                        'Access-Control-Allow-Methods': 'GET',  # Allow only GET method
                        'Access-Control-Allow-Headers': 'Content-Type'  # Allow specific headers
                    },
                    'body': booking_status
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
            'body': 'FAILED'
        }
            
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': 'FAILED'
        }
