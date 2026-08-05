from datetime import datetime
from extensions import db


class IOC(db.Model):
    __tablename__ = 'iocs'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    ioc_type = db.Column(db.String(30), nullable=False)
    ioc_value = db.Column(db.String(500), nullable=False, index=True)
    description = db.Column(db.Text)
    threat_level = db.Column(db.String(20), default='medium')
    confidence = db.Column(db.Integer, default=50)
    source = db.Column(db.String(200))
    first_seen = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    status = db.Column(db.String(30), default='active')
    tags = db.Column(db.String(500))
    related_malware = db.Column(db.String(200))
    related_campaign = db.Column(db.String(200))
    tlp_level = db.Column(db.String(10), default='amber')
    is_shared = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'ioc_type': self.ioc_type,
            'ioc_value': self.ioc_value,
            'description': self.description,
            'threat_level': self.threat_level,
            'confidence': self.confidence,
            'source': self.source,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'status': self.status,
            'tags': self.tags,
            'tlp_level': self.tlp_level,
            'is_shared': self.is_shared,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<IOC {self.ioc_type}:{self.ioc_value}>'