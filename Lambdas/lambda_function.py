import boto3
import json
import os

# AWS clients
sqs_client = boto3.client('sqs')
lambda_client = boto3.client('lambda')

# Environment variables
QUEUE_URL = os.environ['QUEUE_URL']  # SQS Queue URL
BOOKING_REQUEST_LAMBDA = os.environ['BOOKING_REQUEST_LAMBDA']  # Booking Lambda name

def lambda_handler(event, context):
    """
    Virtual waiting room Lambda triggered by SQS to forward ticket requests to the booking_request Lambda.
    """
    print("Received SQS Event:", json.dumps(event))
    
    for record in event['Records']:
        try:
            # Parse the SQS message body
            message_body = json.loads(record['body'])
            print("Processing message:", message_body)
            
            # Extract event_id and seat_no
            event_id = message_body.get("event_id")
            seat_no = message_body.get("seat_no")
            
            if not event_id or not seat_no:
                print("Invalid message format. Skipping...")
                continue
            
            # Forward the message to booking_request Lambda
            response = lambda_client.invoke(
                FunctionName=BOOKING_REQUEST_LAMBDA,
                InvocationType='RequestResponse',  # Ensure synchronous invocation for success confirmation
                Payload=json.dumps({
                    "event_id": event_id,
                    "seat_no": seat_no,
                    "user_id": message_body.get("user_id")  # Optional: Include user info if available
                })
            )
            
            # Check booking_request Lambda response
            booking_response = json.loads(response['Payload'].read().decode('utf-8'))
            if booking_response.get("statusCode") == 200:
                print(f"Successfully processed booking for event_id: {event_id}, seat_no: {seat_no}")
                
                # Delete the message from the queue
                sqs_client.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=record['receiptHandle']
                )
            else:
                print(f"Booking request failed for event_id: {event_id}, seat_no: {seat_no}. Response: {booking_response}")
        
        except Exception as e:
            print(f"Error processing message: {record['messageId']}, Error: {str(e)}")
            # Let the message stay in the queue for retries

    return {
        "statusCode": 200,
        "body": "Virtual waiting room processed messages."
    }