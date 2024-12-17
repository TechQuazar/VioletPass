import json
import os
import psycopg2

def lambda_handler(event, context):
    """Lambda function to reset bookings and ticket statuses"""
    
    # Database connection parameters
    DB_PARAMS = {
        'dbname': os.environ['DB_NAME'],
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'host': os.environ['DB_HOST'],
        'port': os.environ['DB_PORT']
    }
    
    conn = None
    cur = None
    
    try:
        # Establish connection
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Start a transaction
        conn.autocommit = False
        
        # Step 1: Delete all bookings
        cur.execute("DELETE FROM bookings")
        deleted_count = cur.rowcount
        print(f"Deleted {deleted_count} bookings.")
        
        # Step 2: Reset all tickets to 'available'
        cur.execute("""
            UPDATE tickets
            SET status = 'available'
            WHERE status IN ('locked', 'booked')
        """)
        tickets_reset_count = cur.rowcount
        print(f"Reset status for {tickets_reset_count} tickets.")
        
        # Step 3: Update events to reset available ticket count
        cur.execute("""
            UPDATE events
            SET available_tickets = total_tickets
        """)
        events_updated_count = cur.rowcount
        print(f"Updated available tickets for {events_updated_count} events.")
        
        # Commit the transaction
        conn.commit()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "System reset successfully",
                "bookings_deleted": deleted_count,
                "tickets_reset": tickets_reset_count,
                "events_updated": events_updated_count
            })
        }
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps(f'Database error: {str(e)}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
