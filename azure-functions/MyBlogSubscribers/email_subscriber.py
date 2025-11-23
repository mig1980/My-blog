import os
from datetime import datetime
from azure.data.tables import TableClient, TableEntity
from azure.core.exceptions import ResourceExistsError

TABLE_NAME = "subscribers"
PARTITION_KEY = "subscriber"

class SubscriptionError(Exception):
    """Custom exception for subscription-related errors."""
    pass

def get_table_client():
    """
    Get Azure Table Storage client for subscribers table.
    
    Reads STORAGE_CONNECTION_STRING from environment variables and creates
    a TableClient instance for the subscribers table.
    
    Returns:
        TableClient: Configured client for table operations
        
    Raises:
        SubscriptionError: If STORAGE_CONNECTION_STRING is not configured
    """
    conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise SubscriptionError("Storage connection not configured")
    return TableClient.from_connection_string(conn_str, TABLE_NAME)

def subscribe_email(email: str) -> dict:
    """
    Add a new email subscriber to the table.
    
    Creates a new entity in Azure Table Storage with the subscriber's email.
    Uses email (lowercase) as both RowKey for uniqueness and searchable field.
    Handles duplicate subscriptions gracefully by catching ResourceExistsError.
    
    Args:
        email: Email address to subscribe (will be converted to lowercase)
        
    Returns:
        dict: Status dictionary with keys:
            - status: "created" if new subscriber, "exists" if already subscribed
            - message: User-friendly message about the operation result
            
    Raises:
        SubscriptionError: If table client cannot be initialized
    """
    table = get_table_client()
    
    # Create new subscriber entity
    entity = TableEntity()
    entity["PartitionKey"] = PARTITION_KEY  # Fixed partition for all subscribers
    entity["RowKey"] = email.lower()        # Email as unique identifier
    entity["email"] = email.lower()         # Searchable email field
    entity["subscribedAt"] = datetime.utcnow().isoformat()  # Timestamp
    entity["isActive"] = True               # Active by default

    try:
        # Attempt to create the entity
        table.create_entity(entity=entity)
        return {
            "status": "created",
            "message": "Thank you for subscribing! You'll receive weekly updates."
        }
    except ResourceExistsError:
        # Email already exists in table
        return {
            "status": "exists",
            "message": "You're already subscribed!"
        }


def get_active_subscribers() -> list:
    """
    Get all active subscribers from the table.
    
    Queries Azure Table Storage for all entities where:
    - PartitionKey = 'subscriber' (all subscribers)
    - isActive = true (not unsubscribed)
    
    Used by the weekly newsletter job to get the mailing list.
    
    Returns:
        list: List of active subscriber email addresses (lowercase strings)
        
    Raises:
        SubscriptionError: If table client cannot be initialized
    """
    table = get_table_client()
    
    # Query for active subscribers using OData filter syntax
    filter_query = f"PartitionKey eq '{PARTITION_KEY}' and isActive eq true"
    entities = table.query_entities(filter_query)
    
    # Extract just the email addresses from entities
    emails = [entity['email'] for entity in entities]
    
    return emails


def unsubscribe_email(email: str) -> dict:
    """
    Soft unsubscribe - sets isActive to False without deleting the entity.
    
    Performs a soft delete by setting the isActive flag to False, which:
    - Preserves subscription history and data
    - Excludes the email from future newsletter queries
    - Allows potential re-subscription tracking
    
    Args:
        email: Email address to unsubscribe (case-insensitive)
        
    Returns:
        dict: Status dictionary with keys:
            - status: "unsubscribed" on success
            - message: User-friendly confirmation message
            
    Raises:
        SubscriptionError: If email not found or update fails
    """
    from azure.core.exceptions import ResourceNotFoundError
    
    table = get_table_client()
    
    try:
        # Retrieve the existing subscriber entity
        entity = table.get_entity(
            partition_key=PARTITION_KEY,
            row_key=email.lower()
        )
        
        # Set isActive to False (soft delete)
        entity['isActive'] = False
        
        # Update the entity in the table
        table.update_entity(entity, mode='replace')
        
        return {
            "status": "unsubscribed",
            "message": "You've been unsubscribed successfully."
        }
    except ResourceNotFoundError:
        raise SubscriptionError(f"Email not found: {email}")
    except Exception as e:
        # Handle other Azure storage errors
        raise SubscriptionError(f"Failed to unsubscribe {email}: {str(e)}")