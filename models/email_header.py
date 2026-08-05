from datetime import datetime
from extensions import db


class EmailHeaderAnalysis(db.Model):
    __tablename__ = 'email_header_analyses'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    subject = db.Column(db.String(500))
    sender_email = db.Column(db.String(255))
    sender_name = db.Column(db.String(255))
    recipient_email = db.Column(db.String(255))
    reply_to = db.Column(db.String(255))
    date_sent = db.Column(db.DateTime)
    message_id = db.Column(db.String(255))
    received_chain = db.Column(db.Text)
    authentication_results = db.Column(db.Text)
    spf_result = db.Column(db.String(50))
    dkim_result = db.Column(db.String(50))
    dmarc_result = db.Column(db.String(50))
    x_headers = db.Column(db.Text)
    return_path = db.Column(db.String(255))
    envelope_from = db.Column(db.String(255))
    source_ip = db.Column(db.String(45))
    source_hostname = db.Column(db.String(255))
    user_agent = db.Column(db.String(500))
    is_suspicious = db.Column(db.Boolean, default=False)
    spoofing_detected = db.Column(db.Boolean, default=False)
    phishing_indicators = db.Column(db.Text)
    analysis_notes = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'subject': self.subject,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'recipient_email': self.recipient_email,
            'reply_to': self.reply_to,
            'date_sent': self.date_sent.isoformat() if self.date_sent else None,
            'message_id': self.message_id,
            'spf_result': self.spf_result,
            'dkim_result': self.dkim_result,
            'dmarc_result': self.dmarc_result,
            'source_ip': self.source_ip,
            'source_hostname': self.source_hostname,
            'is_suspicious': self.is_suspicious,
            'spoofing_detected': self.spoofing_detected,
            'severity': self.severity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<EmailHeaderAnalysis {self.subject}>'