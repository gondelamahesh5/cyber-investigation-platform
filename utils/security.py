"""
Security utilities for the Cyber Investigation Platform
"""
import re
import hashlib
from datetime import datetime, timedelta
from flask import request, abort
from functools import wraps
from werkzeug.security import safe_join
import os

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent path traversal"""
        filename = os.path.basename(filename)
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return filename
    
    @staticmethod
    def validate_file_type(filepath, allowed_types):
        """Validate file type using magic numbers"""
        import magic
        file_type = magic.from_file(filepath, mime=True)
        return file_type in allowed_types
    
    @staticmethod
    def calculate_file_hash(filepath, algorithm='sha256'):
        """Calculate file hash for integrity verification"""
        hash_func = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    @staticmethod
    def validate_ip_address(ip):
        """Validate IP address format"""
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        return bool(re.match(ipv4_pattern, ip)) or bool(re.match(ipv6_pattern, ip))
    
    @staticmethod
    def validate_url(url):
        """Validate URL format"""
        url_pattern = r'^https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?$'
        return bool(re.match(url_pattern, url))
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def mask_sensitive_data(data, fields=['password', 'ssn', 'credit_card']):
        """Mask sensitive data in logs"""
        if isinstance(data, dict):
            masked = data.copy()
            for field in fields:
                if field in masked:
                    masked[field] = '***MASKED***'
            return masked
        return data


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_rate_limited(self, key, max_requests=10, window=60):
        """Check if request is rate limited"""
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < timedelta(seconds=window)
        ]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            return True
        
        # Add current request
        self.requests[key].append(now)
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP or user ID)
            if current_user.is_authenticated:
                key = f"user_{current_user.id}"
            else:
                key = f"ip_{request.remote_addr}"
            
            if rate_limiter.is_rate_limited(key, max_requests, window):
                abort(429, description="Too many requests. Please try again later.")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(*roles):
    """Role-based access control decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401, description="Authentication required")
            
            if not current_user.has_role(*roles):
                abort(403, description="Insufficient permissions")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_log(action, resource_type):
    """Audit logging decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from models.audit import AuditLog
            from extensions import db
            
            result = f(*args, **kwargs)
            
            try:
                # Get resource ID from kwargs or result
                resource_id = kwargs.get('id') or kwargs.get('case_id') or kwargs.get('evidence_id')
                
                # Create audit log
                audit = AuditLog(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=str(request.form) if request.form else None,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                db.session.add(audit)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Log error but don't fail the request
                print(f"Audit logging failed: {str(e)}")
            
            return result
        return decorated_function
    return decorator


def validate_csrf_token(token):
    """Validate CSRF token"""
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(token)
        return True
    except:
        return False


def prevent_sql_injection(value):
    """Basic SQL injection prevention"""
    if isinstance(value, str):
        # Remove SQL injection patterns
        dangerous_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|\#|\/\*|\*\/)",
            r"(;|\b(OR|AND)\b\s*\d+\s*=\s*\d+)",
            r"(\b(CHAR|NCHAR|VARCHAR|NVARCHAR)\b\s*\()"
        ]
        
        for pattern in dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
    
    return value


def sanitize_html(html):
    """Sanitize HTML to prevent XSS"""
    import bleach
    
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
    ]
    
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt'],
        '*': ['class', 'style']
    }
    
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def generate_secure_token(length=32):
    """Generate cryptographically secure token"""
    import secrets
    return secrets.token_urlsafe(length)


def encrypt_sensitive_data(data, key):
    """Encrypt sensitive data"""
    from cryptography.fernet import Fernet
    
    if isinstance(key, str):
        key = key.encode()
    
    f = Fernet(key)
    encrypted = f.encrypt(data.encode() if isinstance(data, str) else data)
    return encrypted.decode()


def decrypt_sensitive_data(encrypted_data, key):
    """Decrypt sensitive data"""
    from cryptography.fernet import Fernet
    
    if isinstance(key, str):
        key = key.encode()
    
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data.encode() if isinstance(encrypted_data, str) else encrypted_data)
    return decrypted.decode()


def check_password_strength(password):
    """Check password strength"""
    score = 0
    feedback = []
    
    if len(password) < 8:
        feedback.append("Password must be at least 8 characters")
    else:
        score += 1
    
    if not any(c.isupper() for c in password):
        feedback.append("Password must contain uppercase letter")
    else:
        score += 1
    
    if not any(c.islower() for c in password):
        feedback.append("Password must contain lowercase letter")
    else:
        score += 1
    
    if not any(c.isdigit() for c in password):
        feedback.append("Password must contain number")
    else:
        score += 1
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        feedback.append("Password must contain special character")
    else:
        score += 1
    
    strength = 'weak'
    if score >= 4:
        strength = 'strong'
    elif score >= 3:
        strength = 'medium'
    elif score >= 2:
        strength = 'fair'
    
    return {
        'score': score,
        'strength': strength,
        'feedback': feedback
    }


def validate_input(value, input_type, max_length=None):
    """Validate and sanitize user input"""
    if value is None:
        return None
    
    # Sanitize
    value = str(value).strip()
    
    # Length check
    if max_length and len(value) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")
    
    # Type-specific validation
    if input_type == 'email':
        if not SecurityUtils.validate_email(value):
            raise ValueError("Invalid email format")
    elif input_type == 'ip':
        if not SecurityUtils.validate_ip_address(value):
            raise ValueError("Invalid IP address format")
    elif input_type == 'url':
        if not SecurityUtils.validate_url(value):
            raise ValueError("Invalid URL format")
    
    # Prevent SQL injection
    value = prevent_sql_injection(value)
    
    return value