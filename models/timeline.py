from datetime import datetime
from extensions import db


class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    event_title = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.String(50))
    event_source = db.Column(db.String(200))
    related_evidence_id = db.Column(db.Integer, db.ForeignKey('evidence.id'))
    related_ioc_id = db.Column(db.Integer, db.ForeignKey('iocs.id'))
    importance = db.Column(db.String(20), default='normal')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'event_title': self.event_title,
            'event_description': self.event_description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'event_type': self.event_type,
            'event_source': self.event_source,
            'importance': self.importance,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<TimelineEvent {self.event_title}>'