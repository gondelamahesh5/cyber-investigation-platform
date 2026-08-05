from datetime import datetime
from extensions import db


class LinkAnalysis(db.Model):
    __tablename__ = 'link_analyses'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    analysis_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    graph_data = db.Column(db.Text)
    nodes_count = db.Column(db.Integer, default=0)
    edges_count = db.Column(db.Integer, default=0)
    central_nodes = db.Column(db.Text)
    communities = db.Column(db.Text)
    analysis_type = db.Column(db.String(50), default='network')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'analysis_name': self.analysis_name,
            'description': self.description,
            'nodes_count': self.nodes_count,
            'edges_count': self.edges_count,
            'analysis_type': self.analysis_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<LinkAnalysis {self.analysis_name}>'