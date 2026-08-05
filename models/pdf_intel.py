from datetime import datetime
from extensions import db


class PDFIntelligence(db.Model):
    __tablename__ = 'pdf_intelligence'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.BigInteger)
    page_count = db.Column(db.Integer, default=0)
    pdf_metadata = db.Column(db.Text)
    extracted_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    entities_found = db.Column(db.Text)
    urls_found = db.Column(db.Text)
    emails_found = db.Column(db.Text)
    phone_numbers = db.Column(db.Text)
    dates_found = db.Column(db.Text)
    is_malicious = db.Column(db.Boolean, default=False)
    javascript_detected = db.Column(db.Boolean, default=False)
    embedded_files = db.Column(db.Text)
    suspicious_indicators = db.Column(db.Text)
    status = db.Column(db.String(30), default='processed')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'is_malicious': self.is_malicious,
            'javascript_detected': self.javascript_detected,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<PDFIntelligence {self.file_name}>'