import psycopg2
import os
import json
import redis
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
# from opensearchpy.helpers import bulk
# from opensearchpy import OpenSearch
# print('Hi')

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

# OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
# OPENSEARCH_USERNAME = os.environ['OPENSEARCH_USERNAME']
# OPENSEARCH_PASSWORD = os.environ['OPENSEARCH_PASSWORD']

# os_client = OpenSearch(
#         hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
#         http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
#         use_ssl=True,
#         verify_certs=True
#     )

def is_valid_uuid(value):
    """Check if the value is a valid UUID."""
    try:
        UUID(value)
        return True
    except ValueError:
        return False

def decimal_to_str(value):
    """Convert Decimal to string for JSON serialization."""
    if isinstance(value, Decimal):
        return str(value)
    return value

def lambda_handler(event, context):
    """Handle requests for event and ticket management."""
    print('Received Event:', event)
    http_method = event.get("httpMethod", "").upper()
    # try:
    #     events = fetch_events()
    #     print("Events",events)
    #     index_events(events)
    #     print('After Index')
    # except Exception as e:
    #     return {
    #         'statusCode': 500,
    #         'headers': {
    #             'Access-Control-Allow-Origin': '*',
    #             'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
    #             'Access-Control-Allow-Headers': 'Content-Type',
    #         },
    #         'body': json.dumps({"error": str(e)})
    #     }
    # return {
    #         'statusCode': 200,
    #         'headers': {
    #             'Access-Control-Allow-Origin': '*',
    #             'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
    #             'Access-Control-Allow-Headers': 'Content-Type',
    #         },
    #         'body': json.dumps({"status": 'success'})
    #     }
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        if http_method == "GET":
            # Fetch all events
            event_query = "SELECT * FROM events;"
            # event_query = "SELECT * FROM bookings;"
            cur.execute(event_query)
            event_columns = [desc[0] for desc in cur.description]
            events = [
                {key: (value.isoformat() if isinstance(value, datetime) else value)
                 for key, value in zip(event_columns, row)}
                for row in cur.fetchall()
            ]

            # Fetch available seats for each event
            all_event_seats = {}
            for event in events:
                event_id = event["event_id"]
                if not is_valid_uuid(event_id):
                    continue  # Skip invalid event IDs

                # Query all seats for the current event
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

                # Add all seats to the event
                all_event_seats[event_id] = all_seats

            for event in events:
                event_id = event['event_id']
                event['seats'] = all_event_seats[event_id]


            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps(events)
            }
        elif http_method == "POST":
            # Start a transaction
            conn.autocommit = False
            try:
                # Handle POST request (Create a new event)
                body = json.loads(event.get("body", "{}"))
                print('Body',body)
                query = """
                    INSERT INTO events (venue, location, category, total_tickets, available_tickets, start_date, end_date, description, name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING event_id;
                """
                params = (
                    body.get("venue"),
                    body.get("location"),
                    body.get("category"),
                    body.get("total_tickets"),
                    body.get("total_tickets"),  # Initially, available_tickets = total_tickets
                    body.get("start_date"),     # Expected in ISO format: YYYY-MM-DDTHH:MM:SS
                    body.get("end_date"),       # Expected in ISO format: YYYY-MM-DDTHH:MM:SS
                    body.get("description"),
                    body.get("name"),
                )
                cur.execute(query, params)
                event_id = cur.fetchone()[0]
                populate_tickets_table(cur,event_id,body.get("total_tickets"))
                conn.commit()

                # Index the event in OpenSearch
                try:
                    index_event_in_opensearch({
                        "event_id": event_id,
                        "name": body.get("name"),
                        "venue": body.get("venue"),
                        "location": body.get("location"),
                        "category": body.get("category"),
                        "start_date": body.get("start_date"),
                        # "end_date": body.get("end_date"),
                        # "description": body.get("description"),
                        # "total_tickets": body.get("total_tickets"),
                        # "available_tickets": body.get("total_tickets")
                    })
                except Exception as e:
                    print(f"Failed to index event in OpenSearch: {e}")


                return {
                    'statusCode': 201,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                        'Access-Control-Allow-Headers': 'Content-Type',
                    },
                    'body': json.dumps({"message": "Event created successfully", "event_id": event_id})
                }

            except Exception as e:
                conn.rollback()
                print(f"Transaction rolled back due to error: {e}")
                raise

        # Handle CORS preflight requests
        elif http_method == "OPTIONS":
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
            }

        else:
            # Unsupported HTTP method
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps({"error": "Method Not Allowed"})
            }

    except Exception as e:
        # General error handler
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({"error": str(e)})
        }

   
def generate_seat_numbers(total_tickets, seats_per_row=10):
    seat_numbers = []
    rows = (total_tickets + seats_per_row - 1) // seats_per_row  # Total rows needed

    def get_row_label(row):
        label = ""
        while row >= 0:
            label = chr(65 + (row % 26)) + label  # Convert to A-Z
            row = row // 26 - 1
        return label

    for i in range(rows):
        row_label = get_row_label(i)  # Generate row labels (A, B, ..., Z, AA, AB, ...)
        for j in range(1, seats_per_row + 1):
            seat_numbers.append(f"{row_label}{j}")
            if len(seat_numbers) == total_tickets:
                return seat_numbers


def populate_tickets_table(cur, event_id, total_tickets, seats_per_row=10, default_cost=50):
    # Generate seat numbers
    seat_numbers = generate_seat_numbers(total_tickets, seats_per_row)

    # Calculate total rows
    total_rows = (total_tickets + seats_per_row - 1) // seats_per_row  # Total rows needed

    # Insert tickets with calculated categories
    try:
        for seat_no in seat_numbers:
            # Determine row label and index
            row_label = ''.join(filter(str.isalpha, seat_no))  # Extract row label (e.g., 'A' from 'A1')
            row_index = ord(row_label[-1]) - 65 + (26 * (len(row_label) - 1))  # Convert row to index (A=0, B=1,...)
            ticket_cost = default_cost
            # Assign category based on row count
            if total_rows < 3:
                category = 'basic'  # All rows are basic if less than 3 rows
            elif total_rows in [4, 5]:
                if row_index == total_rows - 1:
                    category = 'luxury'  # Last row is luxury
                    ticket_cost = 200
                elif row_index == total_rows - 2:
                    category = 'premium'  # Second last row is premium
                    ticket_cost = 100
                else:
                    category = 'basic'  # Remaining rows are basic
            else:  # total_rows >= 6
                if row_index == total_rows - 1:
                    category = 'luxury'  # Last row is luxury
                elif row_index in [total_rows - 2, total_rows - 3]:
                    category = 'premium'  # Second and third last rows are premium
                else:
                    category = 'basic'  # Remaining rows are basic

            # Insert ticket into the table
            cur.execute("""
                INSERT INTO tickets (event_id, seat_no, category, cost, status)
                VALUES (%s, %s, %s, %s, %s);
            """, (event_id, seat_no, category, ticket_cost,'available'))
        print(f"Successfully inserted {total_tickets} tickets for event_id {event_id}")
    except Exception as e:
        print(f"Error inserting tickets: {e}")
        raise

def index_event_in_opensearch(event_data):
    """Indexes a new event into OpenSearch."""
    OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
    INDEX = "events"
    
    url = f"{OPENSEARCH_ENDPOINT}/{INDEX}/_doc/{event_data['event_id']}"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers, data=json.dumps(event_data))
    response.raise_for_status()
    print(f"Event indexed successfully in OpenSearch: {event_data['event_id']}")


def fetch_events():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    # cur.execute("SELECT * FROM events;")
    cur.execute("SELECT name, event_id, venue, location, start_date, category FROM events;")
    event_columns = [desc[0] for desc in cur.description]
    # events = [dict(zip(columns, row)) for row in cur.fetchall()]
    events = [
                {key: (value.isoformat() if isinstance(value, datetime) else value)
                 for key, value in zip(event_columns, row)}
                for row in cur.fetchall()
            ]
    conn.close()
    return events

def index_events(events):
    # OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
    INDEX = "events"
    # url = f"{OPENSEARCH_ENDPOINT}/{INDEX}/_bulk"
    # headers = {"Content-Type": "application/json"}
    # bulk_data = 

    bulk_data = []
    for event in events:
        doc_id = event["event_id"]  # Assuming event_id is the unique identifier
        bulk_data.append({
            "_op_type": "index",
            "_index": INDEX,
            "_id": doc_id,
            "_source": event
        })
    
    # for event in events:
    #     doc_id = event["event_id"]  # Assuming event_id is the unique identifier
    #     bulk_data += json.dumps({"index": {"_index": INDEX, "_id": doc_id}}) + "\n"
    #     bulk_data += json.dumps(event) + "\n"
    print('Bult data',bulk_data)
    success, failed = bulk(os_client, bulk_data)
    print(f"Successfully indexed: {success}, Failed: {failed}")
    # response = requests.post(url, headers=headers, data=bulk_data,auth=HTTPBasicAuth(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD))
    # response.raise_for_status()
    # print(f"Indexing response: {response.json()}")