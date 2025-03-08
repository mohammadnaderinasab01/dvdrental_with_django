from datetime import datetime
from django.core import exceptions

DATE_FORMATS = [
    '%Y-%m-%d',              # 2025-03-08
    '%Y-%m-%d %H:%M:%S',     # 2025-03-08 14:30:00
    '%Y-%m-%dT%H:%M:%S',     # 2025-03-08T14:30:00 (ISO format)
]


def parse_date(date_str):
    """Try parsing date string with multiple formats"""
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    raise exceptions.ValidationError(f'Invalid date format. Supported formats: {", ".join(DATE_FORMATS)}')
