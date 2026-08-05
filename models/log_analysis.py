from datetime import datetime
from extensions import db


class LogAnalysis(db.Model):
    __tablename__ = 'log_analyses'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    log_type = db.Column(db.String(50), nullable=False)
    log_source = db.Column(db.String(200))
    file_name = db.Column(db.String(255))
    total_entries = db.Column(db.Integer, default=0)
    suspicious_entries = db.Column(db.Integer, default=0)
    analysis_results = db.Column(db.Text)
    anomalies_found = db.Column(db.Text)
    patterns_detected = db.Column(db.Text)
    ip_addresses = db.Column(db.Text)
    user_agents = db.Column(db.Text)
    failed_logins = db.Column(db.Integer, default=0)
    successful_logins = db.Column(db.Integer, default=0)
    brute_force_attempts = db.Column(db.Integer, default=0)
    sql_injection_attempts = db.Column(db.Integer, default=0)
    xss_attempts = db.Column(db.Integer, default=0)
    port_scan_attempts = db.Column(db.Integer, default=0)
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(30), default='analyzed')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'log_type': self.log_type,
            'log_source': self.log_source,
            'file_name': self.file_name,
            'total_entries': self.total_entries,
            'suspicious_entries': self.suspicious_entries,
            'failed_logins': self.failed_logins,
            'successful_logins': self.successful_logins,
            'brute_force_attempts': self.brute_force_attempts,
            'sql_injection_attempts': self.sql_injection_attempts,
            'xss_attempts': self.xss_attempts,
            'port_scan_attempts': self.port_scan_attempts,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<LogAnalysis {self.log_type}>'