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