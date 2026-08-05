from datetime import datetime
from extensions import db


class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default='open')
    priority = db.Column(db.String(20), nullable=False, default='medium')
    classification = db.Column(db.String(50))
    case_type = db.Column(db.String(50))
    severity = db.Column(db.String(20), default='low')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_date = db.Column(db.DateTime)
    opened_date = db.Column(db.DateTime, default=datetime.utcnow)
    closed_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    jurisdiction = db.Column(db.String(100))
    victim_name = db.Column(db.String(120))
    victim_contact = db.Column(db.String(120))
    suspect_name = db.Column(db.String(120))
    suspect_contact = db.Column(db.String(120))
    financial_loss = db.Column(db.Numeric(15, 2), default=0)
    currency = db.Column(db.String(10), default='USD')
    summary = db.Column(db.Text)
    tags = db.Column(db.String(500))
    is_confidential = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidences = db.relationship('Evidence', backref='case', lazy=True, cascade='all, delete-orphan')
    iocs = db.relationship('IOC', backref='case', lazy=True, cascade='all, delete-orphan')
    timeline_events = db.relationship('TimelineEvent', backref='case', lazy=True, cascade='all, delete-orphan')
    link_analyses = db.relationship('LinkAnalysis', backref='case', lazy=True, cascade='all, delete-orphan')
    malware_analyses = db.relationship('MalwareAnalysis', backref='case', lazy=True, cascade='all, delete-orphan')
    log_analyses = db.relationship('LogAnalysis', backref='case', lazy=True, cascade='all, delete-orphan')
    email_analyses = db.relationship('EmailHeaderAnalysis', backref='case', lazy=True, cascade='all, delete-orphan')
    ocr_documents = db.relationship('OCRDocument', backref='case', lazy=True, cascade='all, delete-orphan')
    pdf_intelligence = db.relationship('PDFIntelligence', backref='case', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='case', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'case_number': self.case_number,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'classification': self.classification,
            'case_type': self.case_type,
            'severity': self.severity,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'opened_date': self.opened_date.isoformat() if self.opened_date else None,
            'closed_date': self.closed_date.isoformat() if self.closed_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'location': self.location,
            'jurisdiction': self.jurisdiction,
            'victim_name': self.victim_name,
            'suspect_name': self.suspect_name,
            'financial_loss': float(self.financial_loss) if self.financial_loss else 0,
            'currency': self.currency,
            'summary': self.summary,
            'tags': self.tags,
            'is_confidential': self.is_confidential,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Case {self.case_number}>'