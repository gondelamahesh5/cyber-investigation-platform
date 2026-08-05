from datetime import datetime
from extensions import db


class BackupRecord(db.Model):
    __tablename__ = 'backup_records'

    id = db.Column(db.Integer, primary_key=True)
    backup_name = db.Column(db.String(200), nullable=False)
    backup_type = db.Column(db.String(20), default='full')
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.BigInteger)
    status = db.Column(db.String(30), default='completed')
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'backup_name': self.backup_name,
            'backup_type': self.backup_type,
            'file_size': self.file_size,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f'<BackupRecord {self.backup_name}>'