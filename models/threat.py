from datetime import datetime
from extensions import db


class ThreatIntel(db.Model):
    __tablename__ = 'threat_intel'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    threat_type = db.Column(db.String(50))
    severity = db.Column(db.String(20), default='medium')
    confidence = db.Column(db.Integer, default=50)
    source = db.Column(db.String(200))
    source_url = db.Column(db.String(500))
    published_date = db.Column(db.DateTime)
    first_seen = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    affected_platforms = db.Column(db.String(500))
    attack_vector = db.Column(db.String(200))
    impact = db.Column(db.Text)
    mitigation = db.Column(db.Text)
    indicators = db.Column(db.Text)
    related_campaigns = db.Column(db.String(500))
    tlp_level = db.Column(db.String(10), default='amber')
    status = db.Column(db.String(30), default='active')
    tags = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'confidence': self.confidence,
            'source': self.source,
            'source_url': self.source_url,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'affected_platforms': self.affected_platforms,
            'attack_vector': self.attack_vector,
            'impact': self.impact,
            'mitigation': self.mitigation,
            'indicators': self.indicators,
            'tlp_level': self.tlp_level,
            'status': self.status,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ThreatIntel {self.title}>'