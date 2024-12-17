import json
import uuid
import boto3

# Initialize the SQS client
sqs = boto3.client('sqs')

# Replace with your SQS queue URL
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/182399724631/pay_request.fifo"

def lambda_handler(event, context):
    try:
        # Extract payment details from the event
        reserve_id = event['reserve_id']
        card_number = event['card_number']
        name_on_card = event['name_on_card']
        expiry_date = event['expiry_date']
        email_id = event['email_id']
        cvv = event['cvv']
        user_id = event['user_id']
        event_id = event['event_id']
        seat_numbers = event['seat_numbers']  # Expected to be an array

        # Generate a new payment reference ID
        payment_reference_id = str(uuid.uuid4())

        # Create the payload to send to SQS
        payment_details = {
            "payment_id": payment_reference_id,
            "reserve_id": reserve_id,
            "card_number": card_number,
            "name_on_card": name_on_card,
            "expiry_date": expiry_date,
            "cvv": cvv,
            "email_id": email_id,
            "user_id": user_id,
            "event_id": event_id,
            "seat_numbers": seat_numbers
        }

        # Generate a deduplication ID for FIFO queue
        deduplication_id = str(uuid.uuid4())

        # Send the details to the SQS queue
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(payment_details),
            MessageGroupId="payment-processing-group",  # Required for FIFO queues
            MessageDeduplicationId=deduplication_id  # Required for FIFO queues if ContentBasedDeduplication is not enabled
        )

        # Return the payment reference ID to the user
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Request for Payment has been sent. use the payment referernce id in case of any issues",
                "payment_reference_id": payment_reference_id
            })
        }

    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                "error": f"Missing required field: {str(e)}"
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                "error": str(e)
            })
        }
