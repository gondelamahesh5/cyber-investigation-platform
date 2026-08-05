"""
Logging configuration for enterprise deployment
"""
import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import current_app, request
from datetime import datetime

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information"""
    
    def format(self, record):
        record.url = request.url if request else 'N/A'
        record.remote_addr = request.remote_addr if request else 'N/A'
        record.method = request.method if request else 'N/A'
        return super().format(record)

def setup_logging(app):
    """Configure logging for the application"""
    
    if not os.path.exists(app.config['LOG_FOLDER']):
        os.makedirs(app.config['LOG_FOLDER'])
    
    # Formatters
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    
    # Error log handler (errors and above)
    error_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_FOLDER'], 'error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Info log handler (info and above)
    info_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_FOLDER'], 'info.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    
    # Security log handler
    security_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_FOLDER'], 'security.log'),
        maxBytes=10485760,
        backupCount=10
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(formatter)
    
    # Console handler for development
    if app.config['DEBUG']:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
    
    # Add handlers to app logger
    app.logger.addHandler(error_handler)
    app.logger.addHandler(info_handler)
    app.logger.addHandler(security_handler)
    app.logger.setLevel(logging.INFO)
    
    # SQLAlchemy logging (optional, for debugging)
    if app.config.get('SQLALCHEMY_ECHO'):
        sql_logger = logging.getLogger('sqlalchemy.engine')
        sql_logger.setLevel(logging.INFO)
        sql_handler = RotatingFileHandler(
            os.path.join(app.config['LOG_FOLDER'], 'sql.log'),
            maxBytes=10485760,
            backupCount=5
        )
        sql_handler.setFormatter(formatter)
        sql_logger.addHandler(sql_handler)
    
    # Email handler for critical errors (production)
    if not app.config['DEBUG'] and app.config.get('MAIL_SERVER'):
        auth = None
        if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_DEFAULT_SENDER'],
            toaddrs=[app.config['ADMIN_EMAIL']],
            subject='Cyber Investigation Platform - Critical Error',
            credentials=auth,
            secure=() if app.config.get('MAIL_USE_TLS') else None
        )
        mail_handler.setLevel(logging.CRITICAL)
        mail_handler.setFormatter(formatter)
        app.logger.addHandler(mail_handler)
    
    return app.logger


def log_security_event(app, event_type, details, severity='warning'):
    """Log security-related events"""
    security_logger = logging.getLogger('security')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'severity': severity
    }
    
    if severity == 'critical':
        security_logger.critical(f"Security Event: {log_data}")
    elif severity == 'warning':
        security_logger.warning(f"Security Event: {log_data}")
    else:
        security_logger.info(f"Security Event: {log_data}")


def log_user_activity(app, user_id, action, resource_type, resource_id=None, details=None):
    """Log user activity for audit trail"""
    activity_logger = logging.getLogger('user_activity')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'details': details,
        'ip_address': request.remote_addr if request else 'N/A',
        'user_agent': request.user_agent.string if request else 'N/A'
    }
    
    activity_logger.info(f"User Activity: {log_data}")