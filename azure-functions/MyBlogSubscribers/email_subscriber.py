import os
from datetime import datetime
from azure.data.tables import TableClient, TableEntity
from azure.core.exceptions import ResourceExistsError

TABLE_NAME = "subscribers"
PARTITION_KEY = "subscriber"

class SubscriptionError(Exception):
    pass

def get_table_client():
    conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise SubscriptionError("Storage connection not configured")
    return TableClient.from_connection_string(conn_str, TABLE_NAME)

def subscribe_email(email: str) -> dict:
    table = get_table_client()
    entity = TableEntity()
    entity["PartitionKey"] = PARTITION_KEY
    entity["RowKey"] = email.lower()
    entity["email"] = email.lower()
    entity["subscribedAt"] = datetime.utcnow().isoformat()
    entity["isActive"] = True

    try:
        table.create_entity(entity=entity)
        return {
            "status": "created",
            "message": "Thank you for subscribing! You'll receive weekly updates."
        }
    except ResourceExistsError:
        return {
            "status": "exists",
            "message": "You're already subscribed!"
        }


def get_active_subscribers() -> list:
    """
    Get all active subscribers from the table.
    
    Returns:
        list: List of active subscriber email addresses
    """
    table = get_table_client()
    
    # Query for active subscribers
    filter_query = f"PartitionKey eq '{PARTITION_KEY}' and isActive eq true"
    entities = table.query_entities(filter_query)
    
    # Extract just the email addresses
    emails = [entity['email'] for entity in entities]
    
    return emails


def unsubscribe_email(email: str) -> dict:
    """
    Soft unsubscribe - sets isActive to False.
    
    Args:
        email: Email address to unsubscribe
        
    Returns:
        dict: Status message
    """
    table = get_table_client()
    
    try:
        # Get the entity
        entity = table.get_entity(
            partition_key=PARTITION_KEY,
            row_key=email.lower()
        )
        
        # Update isActive flag
        entity['isActive'] = False
        table.update_entity(entity, mode='replace')
        
        return {
            "status": "unsubscribed",
            "message": "You've been unsubscribed successfully."
        }
    except Exception as e:
        raise SubscriptionError(f"Failed to unsubscribe: {str(e)}")