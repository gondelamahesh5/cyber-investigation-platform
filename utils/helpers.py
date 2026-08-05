import os
import re
import uuid
import json
from datetime import datetime, timedelta
from flask import current_app


def generate_case_number():
    year = datetime.utcnow().year
    unique = uuid.uuid4().hex[:6].upper()
    return f"CYB-{year}-{unique}"


def generate_evidence_number():
    unique = uuid.uuid4().hex[:8].upper()
    return f"EVD-{unique}"


def generate_report_number():
    unique = uuid.uuid4().hex[:8].upper()
    return f"RPT-{unique}"


def generate_otp():
    import random
    return str(random.randint(100000, 999999))


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    pattern = r'^\+?[0-9\s\-()]{7,20}$'
    return re.match(pattern, phone) is not None


def sanitize_input(text):
    if not text:
        return text
    return re.sub(r'[<>{}]', '', str(text))


def parse_tags(tags_string):
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]


def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    if not dt:
        return 'N/A'
    return dt.strftime(format)


def get_client_ip():
    from flask import request
    return request.remote_addr


def json_serialize(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return str(obj)


def safe_json_loads(text, default=None):
    try:
        return json.loads(text) if text else default
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text, max_length=200):
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


def get_file_icon(filename):
    ext = os.path.splitext(filename)[1].lower() if filename else ''
    icons = {
        '.pdf': 'fa-file-pdf',
        '.png': 'fa-file-image',
        '.jpg': 'fa-file-image',
        '.jpeg': 'fa-file-image',
        '.gif': 'fa-file-image',
        '.txt': 'fa-file-alt',
        '.csv': 'fa-file-csv',
        '.xlsx': 'fa-file-excel',
        '.eml': 'fa-envelope',
        '.zip': 'fa-file-archive',
        '.doc': 'fa-file-word',
        '.docx': 'fa-file-word',
        '.exe': 'fa-file-code',
        '.dll': 'fa-file-code'
    }
    return icons.get(ext, 'fa-file')


def get_status_color(status):
    colors = {
        'open': 'success',
        'closed': 'secondary',
        'pending': 'warning',
        'under_investigation': 'info',
        'active': 'success',
        'inactive': 'secondary',
        'high': 'danger',
        'medium': 'warning',
        'low': 'info',
        'critical': 'danger',
        'collected': 'info',
        'analyzed': 'success',
        'verified': 'success',
        'draft': 'secondary',
        'final': 'success'
    }
    return colors.get(status, 'secondary')


def get_severity_badge(severity):
    colors = {
        'critical': 'danger',
        'high': 'danger',
        'medium': 'warning',
        'low': 'info',
        'info': 'info'
    }
    return colors.get(severity, 'secondary')