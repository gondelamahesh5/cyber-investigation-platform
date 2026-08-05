from datetime import datetime
from extensions import db


class Evidence(db.Model):
    __tablename__ = 'evidence'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    evidence_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    evidence_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(500))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.BigInteger)
    file_hash_md5 = db.Column(db.String(32))
    file_hash_sha1 = db.Column(db.String(40))
    file_hash_sha256 = db.Column(db.String(64))
    mime_type = db.Column(db.String(100))
    source = db.Column(db.String(200))
    collected_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    collected_date = db.Column(db.DateTime)
    collection_method = db.Column(db.String(200))
    chain_of_custody = db.Column(db.Text)
    status = db.Column(db.String(30), default='collected')
    integrity_status = db.Column(db.String(30), default='verified')
    is_encrypted = db.Column(db.Boolean, default=False)
    encryption_method = db.Column(db.String(100))
    storage_location = db.Column(db.String(200))
    retention_date = db.Column(db.DateTime)
    disposition = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploader = db.relationship('User', backref='uploaded_evidence', foreign_keys=[collected_by])

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'evidence_number': self.evidence_number,
            'title': self.title,
            'description': self.description,
            'evidence_type': self.evidence_type,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_hash_md5': self.file_hash_md5,
            'file_hash_sha1': self.file_hash_sha1,
            'file_hash_sha256': self.file_hash_sha256,
            'mime_type': self.mime_type,
            'source': self.source,
            'collected_by': self.collected_by,
            'collected_date': self.collected_date.isoformat() if self.collected_date else None,
            'collection_method': self.collection_method,
            'status': self.status,
            'integrity_status': self.integrity_status,
            'is_encrypted': self.is_encrypted,
            'storage_location': self.storage_location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Evidence {self.evidence_number}>'