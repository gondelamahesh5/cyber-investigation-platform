from datetime import datetime
from flask import request
from extensions import db
from models.audit import AuditLog


def log_action(user_id, action, resource_type=None, resource_id=None, description=None, status='success', details=None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=request.remote_addr if request else None,
        user_agent=request.user_agent.string if request and request.user_agent else None,
        status=status,
        details=details
    )
    db.session.add(audit)
    db.session.commit()
    return audit


def get_audit_logs(page=1, per_page=20, user_id=None, action=None, resource_type=None):
    query = AuditLog.query
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    return query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)