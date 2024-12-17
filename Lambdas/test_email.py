import boto3
import json

# Initialize the SES client
ses_client = boto3.client('ses', region_name='us-east-1')  # Replace 'us-east-1' with your SES region if different

def lambda_handler(event, context):
    """AWS Lambda function to send an email using Amazon SES."""
    source_email = "sidharthareddy02@gmail.com"  # Verified email address in SES
    destination_email = "sidharthareddy02@gmail.com"  # Same as source email
    
    subject = "Test Email from AWS Lambda"
    body_text = "This is a test email sent from AWS Lambda using Amazon SES."

    try:
        # Send the email
        response = ses_client.send_email(
            Source=source_email,
            Destination={
                'ToAddresses': [destination_email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    }
                }
            }
        )
        print(f"Email sent successfully! MessageId: {response['MessageId']}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Email sent successfully! MessageId: {response['MessageId']}")
        }
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to send email: {e}")
        }
