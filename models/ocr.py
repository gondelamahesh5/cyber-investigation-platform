from datetime import datetime
from extensions import db


class OCRDocument(db.Model):
    __tablename__ = 'ocr_documents'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))
    extracted_text = db.Column(db.Text)
    confidence_score = db.Column(db.Float, default=0.0)
    language = db.Column(db.String(20), default='eng')
    page_count = db.Column(db.Integer, default=1)
    entities_found = db.Column(db.Text)
    ocr_engine = db.Column(db.String(50), default='tesseract')
    status = db.Column(db.String(30), default='processed')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'file_name': self.file_name,
            'confidence_score': self.confidence_score,
            'language': self.language,
            'page_count': self.page_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<OCRDocument {self.file_name}>'