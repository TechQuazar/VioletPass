import json
import boto3
import uuid
from datetime import datetime

def lambda_handler(event, context):
    # Initialize SQS client
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/182399724631/book_request.fifo'
    print(event)
    try:
        # The event is already a dictionary, no need to parse JSON
        body = event
        
        # Extract booking details
        event_id = body.get('event_id')
        user_id = body.get('user_id')
        seat_numbers = body.get('seat_numbers', [])
        
        # Validate required fields
        if not all([event_id, user_id, seat_numbers]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing required fields: eventId, userId, and seats are required'
                })
            }
        

        # Create message for SQS
        message = {
            'reserve_id': str(uuid.uuid4()),
            'event_id': event_id,
            'user_id': user_id,
            'seat_numbers': seat_numbers
        }
        
        # Send message to SQS
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageGroupId=event_id,  # Using eventId as group ID to maintain order per event
            MessageDeduplicationId=str(uuid.uuid4())  # Unique ID for each message
        )
        print('message sent to queue')
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'reserve request received',
                'reserve_id': message['reserve_id']
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")  # For CloudWatch logs
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Internal server error: lambda error {str(e)}'
            })
        }
