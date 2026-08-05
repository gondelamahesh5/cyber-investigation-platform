from datetime import datetime
from extensions import db


class DocumentSummary(db.Model):
    __tablename__ = 'document_summaries'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    document_type = db.Column(db.String(50))
    document_name = db.Column(db.String(255))
    original_text = db.Column(db.Text)
    summary_text = db.Column(db.Text)
    summary_length = db.Column(db.Integer)
    compression_ratio = db.Column(db.Float)
    key_points = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    language = db.Column(db.String(20), default='en')
    model_used = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'document_type': self.document_type,
            'document_name': self.document_name,
            'summary_text': self.summary_text,
            'summary_length': self.summary_length,
            'compression_ratio': self.compression_ratio,
            'key_points': self.key_points,
            'sentiment': self.sentiment,
            'language': self.language,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<DocumentSummary {self.document_name}>'