import boto3
import requests
import os
import json

def lambda_handler(event, context):
    # OpenSearch configuration
    print('Event,',event,context)
    OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT'] # Add this
    INDEX = "events"
    # http_method = event.get("httpMethod", "").upper()  # Get the HTTP method
    

    # Extract the free-form query from queryStringParameters
    params = event.get("queryStringParameters", {})
    query_string = params.get("q", "").strip()
    page = int(params.get("page", 1))
    limit = int(params.get("limit", 10))
    offset = (page - 1) * limit

    # Build the OpenSearch query
    query = {
        "from": offset,
        "size": limit,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query_string,
                            "fields": [
                                "name^3",  # Higher weight for event name
                                "venue^2", # Medium weight for venue
                                "location^2", # Medium weight for location
                                "start_date" # Lower weight for exact date match
                                "category^2",
                            ],
                            "fuzziness": "AUTO"  # Allow fuzzy matching for typos
                        }
                    }
                ]
            }
        }
    }

    # Execute the OpenSearch query
    try:
        url = f"{OPENSEARCH_ENDPOINT}/{INDEX}/_search"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(query))
        response.raise_for_status()  # Raise exception if query fails
        results = response.json()
        print('Results from opensearch',results)
        # Extract and format results
        events = [
            {
                "_id": hit["_id"],
                **hit["_source"]
            }
            for hit in results["hits"]["hits"]
        ]

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({"events": events})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({"error": str(e)})
        }
