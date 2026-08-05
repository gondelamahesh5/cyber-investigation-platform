import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from config.config import config_map
from extensions import db, login_manager, migrate



def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from models.user import User
    from models.case import Case
    from models.evidence import Evidence
    from models.ioc import IOC
    from models.threat import ThreatIntel
    from models.audit import AuditLog
    from models.notification import Notification
    from models.report import Report
    from models.link import LinkAnalysis
    from models.malware import MalwareAnalysis
    from models.log_analysis import LogAnalysis
    from models.email_header import EmailHeaderAnalysis
    from models.ocr import OCRDocument
    from models.pdf_intel import PDFIntelligence
    from models.timeline import TimelineEvent
    from models.settings import SystemSetting
    from models.backup import BackupRecord
    from models.search import SearchIndex
    from models.entity import ExtractedEntity
    from models.summary import DocumentSummary

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.cases import cases_bp
    from routes.evidence import evidence_bp
    from routes.iocs import iocs_bp
    from routes.threats import threats_bp
    from routes.analysis import analysis_bp
    from routes.reports import reports_bp
    from routes.settings import settings_bp
    from routes.api import api_bp
    from routes.ai_assistant import ai_assistant_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(iocs_bp)
    app.register_blueprint(threats_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(ai_assistant_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.context_processor
    def inject_globals():
        notifications = []
        unread_count = 0
        if current_user.is_authenticated:
            from services.notification_service import get_user_notifications, get_unread_count
            notifications = get_user_notifications(current_user.id, limit=5)
            unread_count = get_unread_count(current_user.id)
        return {
            'notifications': notifications,
            'unread_count': unread_count
        }

    @app.errorhandler(404)
    def not_found(error):
        return redirect(url_for('dashboard.index'))

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return 'Internal Server Error', 500

    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
        os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
        os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)