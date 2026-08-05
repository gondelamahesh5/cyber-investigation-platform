from datetime import datetime
from extensions import db


class SearchIndex(db.Model):
    __tablename__ = 'search_index'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    tags = db.Column(db.String(500))
    search_vector = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'title': self.title,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<SearchIndex {self.entity_type}:{self.entity_id}>'