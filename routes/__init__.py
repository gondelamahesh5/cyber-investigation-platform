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

__all__ = [
    'auth_bp', 'dashboard_bp', 'cases_bp', 'evidence_bp', 'iocs_bp',
    'threats_bp', 'analysis_bp', 'reports_bp', 'settings_bp', 'api_bp'
]