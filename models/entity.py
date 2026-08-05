from datetime import datetime
from extensions import db


class ExtractedEntity(db.Model):
    __tablename__ = 'extracted_entities'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    entity_type = db.Column(db.String(30), nullable=False)
    entity_value = db.Column(db.String(500), nullable=False)
    context = db.Column(db.Text)
    confidence = db.Column(db.Float, default=0.0)
    source_document = db.Column(db.String(255))
    source_type = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'entity_type': self.entity_type,
            'entity_value': self.entity_value,
            'context': self.context,
            'confidence': self.confidence,
            'source_document': self.source_document,
            'source_type': self.source_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ExtractedEntity {self.entity_type}:{self.entity_value}>'