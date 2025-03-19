import sqlparse
from sqlparse.tokens import Keyword, DML
from sqlparse.sql import IdentifierList, Identifier
import uuid


def convert_uuid_to_string(value):
    """
    Recursively converts any uuid.UUID objects in the input value
    to their string representation.
    """
    if isinstance(value, uuid.UUID):
        # Convert UUID to string
        return str(value)
    elif isinstance(value, list):
        # Recursively process each item in the list
        return [convert_uuid_to_string(item) for item in value]
    elif isinstance(value, dict):
        # Recursively process each key-value pair in the dictionary
        return {key: convert_uuid_to_string(val) for key, val in value.items()}
    else:
        # Return the value unchanged
        return value
