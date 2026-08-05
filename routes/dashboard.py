from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import Evidence
from models.ioc import IOC
from models.threat import ThreatIntel
from models.audit import AuditLog
from models.notification import Notification
from services.notification_service import get_unread_count

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    total_cases = Case.query.count()
    open_cases = Case.query.filter_by(status='open').count()
    under_investigation = Case.query.filter_by(status='under_investigation').count()
    closed_cases = Case.query.filter_by(status='closed').count()

    total_evidence = Evidence.query.count()
    total_iocs = IOC.query.count()
    total_threats = ThreatIntel.query.count()

    critical_threats = ThreatIntel.query.filter_by(severity='critical').count()
    high_threats = ThreatIntel.query.filter_by(severity='high').count()

    recent_cases = Case.query.order_by(Case.created_at.desc()).limit(10).all()
    recent_iocs = IOC.query.order_by(IOC.created_at.desc()).limit(5).all()
    recent_activities = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()

    unread_count = get_unread_count(current_user.id)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()

    # Prepare stats for new dashboard
    stats = {
        'total_cases': total_cases,
        'open_cases': open_cases,
        'total_evidence': total_evidence,
        'pending_evidence': Evidence.query.filter_by(status='collected').count(),
        'total_iocs': total_iocs,
        'critical_iocs': IOC.query.filter_by(threat_level='critical').count(),
        'total_threats': total_threats,
        'active_threats': ThreatIntel.query.filter_by(status='active').count(),
    }

    # Chart data - Case Activity (last 7 days)
    from datetime import datetime, timedelta
    days = []
    cases_count = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        days.append(date.strftime('%b %d'))
        count = Case.query.filter(
            db.func.date(Case.created_at) == date.date()
        ).count()
        cases_count.append(count)

    case_activity_chart = {
        'labels': days,
        'data': cases_count
    }

    # Chart data - Priority Distribution
    priority_chart = {
        'labels': ['Critical', 'High', 'Medium', 'Low'],
        'data': [
            Case.query.filter_by(priority='critical').count(),
            Case.query.filter_by(priority='high').count(),
            Case.query.filter_by(priority='medium').count(),
            Case.query.filter_by(priority='low').count()
        ]
    }

    return render_template(
        'dashboard/index.html',
        stats=stats,
        recent_activities=recent_activities,
        unread_count=unread_count,
        notifications=notifications,
        case_activity_chart=case_activity_chart,
        priority_chart=priority_chart
    )
