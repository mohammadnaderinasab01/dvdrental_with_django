from datetime import datetime
from django.core import exceptions

DATE_FORMATS = [
    '%Y-%m-%d',              # 2025-03-08
    '%Y-%m-%d %H:%M:%S',     # 2025-03-08 14:30:00
    '%Y-%m-%dT%H:%M:%S',     # 2025-03-08T14:30:00 (ISO format)
]


def validate_date_format(date_str):
    """Try parsing date string with multiple formats"""
    for date_format in DATE_FORMATS:
        try:
            formatted_date = datetime.strptime(date_str, date_format)
            return
        except ValueError:
            continue
    raise exceptions.ValidationError(f'Invalid date format. Supported formats: {", ".join(DATE_FORMATS)}')
