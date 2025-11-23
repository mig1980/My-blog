import os
import time
import logging
from datetime import datetime
from azure.data.tables import TableClient, TableEntity
from azure.core.exceptions import ResourceExistsError, ServiceRequestError, HttpResponseError
from validation import normalize_email

TABLE_NAME = "subscribers"
PARTITION_KEY = "subscriber"


def retry_table_operation(max_retries=3, initial_delay=0.5, backoff_factor=2.0):
    """
    Decorator that implements exponential backoff retry logic for Azure Table operations.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 0.5)
        backoff_factor: Multiplier for delay on each retry (default: 2.0)
    
    Returns:
        Decorator function that wraps the target function with retry logic
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ServiceRequestError, HttpResponseError, ConnectionError) as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Check if error is retryable
                        is_retryable = False
                        
                        if isinstance(e, HttpResponseError):
                            # Retry on server errors (5xx) or throttling (429)
                            status = getattr(e, 'status_code', 0)
                            is_retryable = status >= 500 or status == 429
                        elif isinstance(e, (ServiceRequestError, ConnectionError)):
                            # Network errors are always retryable
                            is_retryable = True
                        
                        if is_retryable:
                            logging.warning(
                                f"Azure Table operation failed on attempt {attempt + 1}/{max_retries + 1}: "
                                f"{type(e).__name__}: {str(e)}. Retrying in {delay:.1f}s..."
                            )
                            time.sleep(delay)
                            delay *= backoff_factor
                            continue
                    
                    # Non-retryable error or max retries reached
                    raise last_exception
                except ResourceExistsError:
                    # ResourceExistsError is not a failure - just means duplicate subscription
                    raise
                except Exception as e:
                    # Non-retryable exceptions
                    raise e
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


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

@retry_table_operation(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
def _create_entity_with_retry(table, entity):
    """
    Internal function to create table entity with retry logic.
    Separated to allow retry decorator to work properly.
    """
    return table.create_entity(entity=entity)


def subscribe_email(email: str) -> dict:
    """
    Add a new email subscriber to the table with automatic retry on transient failures.
    
    Creates a new entity in Azure Table Storage with the subscriber's email.
    Uses normalized email (lowercase, trimmed) as both RowKey for uniqueness and searchable field.
    Handles duplicate subscriptions gracefully by catching ResourceExistsError.
    
    Args:
        email: Email address to subscribe (will be normalized: trimmed and lowercased)
        
    Returns:
        dict: Status dictionary with keys:
            - status: "created" if new subscriber, "exists" if already subscribed
            - message: User-friendly message about the operation result
            
    Raises:
        SubscriptionError: If table client cannot be initialized or operation fails after retries
    """
    # Normalize email for consistent storage and comparison
    email_normalized = normalize_email(email)
    
    try:
        table = get_table_client()
    except SubscriptionError as e:
        logging.error(f"Failed to get table client for subscription: {str(e)}")
        raise
    
    # Create new subscriber entity
    entity = TableEntity()
    entity["PartitionKey"] = PARTITION_KEY     # Fixed partition for all subscribers
    entity["RowKey"] = email_normalized        # Normalized email as unique identifier
    entity["email"] = email_normalized         # Searchable email field
    entity["subscribedAt"] = datetime.utcnow().isoformat()  # Timestamp
    entity["isActive"] = True                  # Active by default

    try:
        # Attempt to create the entity with retry logic
        _create_entity_with_retry(table, entity)
        
        logging.info(
            f"New subscriber created: {email_normalized}",
            extra={'email': email_normalized, 'action': 'subscribe'}
        )
        
        return {
            "status": "created",
            "message": "Thank you for subscribing! You'll receive weekly updates."
        }
    except ResourceExistsError:
        # Email already exists in table - this is not an error
        logging.info(
            f"Duplicate subscription attempt: {email_normalized}",
            extra={'email': email_normalized, 'action': 'duplicate_subscribe'}
        )
        return {
            "status": "exists",
            "message": "You're already subscribed!"
        }
    except Exception as e:
        logging.error(
            f"Failed to subscribe {email_normalized}: {type(e).__name__}: {str(e)}",
            extra={'email': email_normalized, 'error_type': type(e).__name__}
        )
        raise SubscriptionError(f"Failed to process subscription: {str(e)}")


@retry_table_operation(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
def _query_entities_with_retry(table, filter_query):
    """
    Internal function to query table entities with retry logic.
    Separated to allow retry decorator to work properly.
    """
    return list(table.query_entities(filter_query))


def get_active_subscribers() -> list:
    """
    Get all active subscribers from the table with automatic retry on transient failures.
    
    Queries Azure Table Storage for all entities where:
    - PartitionKey = 'subscriber' (all subscribers)
    - isActive = true (not unsubscribed)
    
    Used by the weekly newsletter job to get the mailing list.
    
    Returns:
        list: List of active subscriber email addresses (lowercase strings)
        
    Raises:
        SubscriptionError: If table client cannot be initialized or query fails after retries
    """
    try:
        table = get_table_client()
    except SubscriptionError as e:
        logging.error(f"Failed to get table client for subscriber query: {str(e)}")
        raise
    
    # Query for active subscribers using OData filter syntax
    filter_query = f"PartitionKey eq '{PARTITION_KEY}' and isActive eq true"
    
    try:
        entities = _query_entities_with_retry(table, filter_query)
        
        # Extract just the email addresses from entities
        emails = [entity['email'] for entity in entities]
        
        logging.info(
            f"Retrieved {len(emails)} active subscribers from table storage",
            extra={'subscriber_count': len(emails)}
        )
        
        return emails
        
    except Exception as e:
        logging.error(
            f"Failed to retrieve active subscribers: {type(e).__name__}: {str(e)}",
            extra={'error_type': type(e).__name__}
        )
        raise SubscriptionError(f"Failed to retrieve subscribers: {str(e)}")


@retry_table_operation(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
def _get_entity_with_retry(table, partition_key, row_key):
    """
    Internal function to get table entity with retry logic.
    """
    return table.get_entity(partition_key=partition_key, row_key=row_key)


@retry_table_operation(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
def _update_entity_with_retry(table, entity, mode):
    """
    Internal function to update table entity with retry logic.
    """
    return table.update_entity(entity, mode=mode)


def unsubscribe_email(email: str) -> dict:
    """
    Soft unsubscribe - sets isActive to False without deleting the entity.
    Includes automatic retry on transient failures.
    
    Performs a soft delete by setting the isActive flag to False, which:
    - Preserves subscription history and data
    - Excludes the email from future newsletter queries
    - Allows potential re-subscription tracking
    
    Args:
        email: Email address to unsubscribe (will be normalized for lookup)
        
    Returns:
        dict: Status dictionary with keys:
            - status: "unsubscribed" on success
            - message: User-friendly confirmation message
            
    Raises:
        SubscriptionError: If email not found or update fails after retries
    """
    from azure.core.exceptions import ResourceNotFoundError
    
    # Normalize email for lookup
    email_normalized = normalize_email(email)
    
    try:
        table = get_table_client()
    except SubscriptionError as e:
        logging.error(f"Failed to get table client for unsubscribe: {str(e)}")
        raise
    
    try:
        # Retrieve the existing subscriber entity with retry
        entity = _get_entity_with_retry(table, PARTITION_KEY, email_normalized)
        
        # Set isActive to False (soft delete)
        entity['isActive'] = False
        
        # Update the entity in the table with retry
        _update_entity_with_retry(table, entity, mode='replace')
        
        logging.info(
            f"Subscriber unsubscribed: {email_normalized}",
            extra={'email': email_normalized, 'action': 'unsubscribe'}
        )
        
        return {
            "status": "unsubscribed",
            "message": "You've been unsubscribed successfully."
        }
    except ResourceNotFoundError:
        logging.warning(
            f"Unsubscribe attempted for non-existent email: {email_normalized}",
            extra={'email': email_normalized, 'action': 'unsubscribe_not_found'}
        )
        raise SubscriptionError(f"Email not found: {email}")
    except Exception as e:
        # Handle other Azure storage errors
        logging.error(
            f"Failed to unsubscribe {email_normalized}: {type(e).__name__}: {str(e)}",
            extra={'email': email_normalized, 'error_type': type(e).__name__}
        )
        raise SubscriptionError(f"Failed to unsubscribe {email}: {str(e)}")