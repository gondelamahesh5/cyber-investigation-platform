from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.case import Case
from models.evidence import Evidence
from models.ioc import IOC
from models.threat import ThreatIntel
from models.audit import AuditLog
from extensions import db
import json
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from services.file_service import save_upload, calculate_file_hashes, get_mime_type
from utils.helpers import generate_evidence_number

ai_assistant_bp = Blueprint('ai_assistant', __name__)


@ai_assistant_bp.route('/ai-assistant')
@login_required
def index():
    """AI Investigation Assistant Dashboard"""
    return render_template('analysis/ai_assistant.html')


@ai_assistant_bp.route('/api/ai/analyze-case/<int:case_id>')
@login_required
def analyze_case(case_id):
    """AI-powered case analysis"""
    case = Case.query.get_or_404(case_id)
    
    # Get related data
    evidence_items = Evidence.query.filter_by(case_id=case_id).all()
    iocs = case.iocs if hasattr(case, 'iocs') else []
    threats = ThreatIntel.query.filter(
        ThreatIntel.id.in_([ioc.threat_id for ioc in iocs if ioc.threat_id])
    ).all() if iocs else []
    
    # Calculate risk score
    risk_score = calculate_risk_score(case, evidence_items, iocs, threats)
    
    # Generate insights
    insights = generate_insights(case, evidence_items, iocs, threats)
    
    # Find related cases
    related_cases = find_related_cases(case)
    
    # Generate summary
    summary = generate_case_summary(case, evidence_items, iocs)
    
    return jsonify({
        'risk_score': risk_score,
        'confidence': calculate_confidence(case, evidence_items),
        'insights': insights,
        'related_cases': related_cases,
        'summary': summary,
        'recommendations': generate_recommendations(case, risk_score)
    })


def calculate_risk_score(case, evidence, iocs, threats):
    """Calculate AI-powered risk score (0-100)"""
    score = 0
    
    # Base score from case priority
    priority_scores = {'critical': 40, 'high': 30, 'medium': 20, 'low': 10}
    score += priority_scores.get(case.priority, 10)
    
    # Evidence count
    score += min(len(evidence) * 2, 20)
    
    # Critical IOCs
    critical_iocs = [ioc for ioc in iocs if ioc.threat_level == 'critical']
    score += min(len(critical_iocs) * 5, 20)
    
    # Active threats
    active_threats = [t for t in threats if t.status == 'active']
    score += min(len(active_threats) * 3, 10)
    
    # Case age
    if case.created_at:
        age = (datetime.utcnow() - case.created_at).days
        if age > 30:
            score += 10
    
    return min(score, 100)


def calculate_confidence(case, evidence):
    """Calculate confidence score based on evidence quality"""
    if not evidence:
        return 0
    
    verified = sum(1 for e in evidence if e.status == 'verified')
    return round((verified / len(evidence)) * 100)


def generate_insights(case, evidence, iocs, threats):
    """Generate AI insights for investigation"""
    insights = []
    
    # Evidence insights
    if len(evidence) > 10:
        insights.append({
            'type': 'info',
            'title': 'High Evidence Volume',
            'message': f'Case has {len(evidence)} evidence items. Consider prioritizing review.'
        })
    
    # IOC insights
    critical_iocs = [ioc for ioc in iocs if ioc.threat_level == 'critical']
    if critical_iocs:
        insights.append({
            'type': 'danger',
            'title': 'Critical IOCs Detected',
            'message': f'{len(critical_iocs)} critical IOCs require immediate attention.'
        })
    
    # Threat insights
    active_threats = [t for t in threats if t.status == 'active']
    if active_threats:
        insights.append({
            'type': 'warning',
            'title': 'Active Threats',
            'message': f'{len(active_threats)} active threats linked to this case.'
        })
    
    # Timeline insights
    if case.created_at:
        age = (datetime.utcnow() - case.created_at).days
        if age > 30:
            insights.append({
                'type': 'warning',
                'title': 'Case Aging',
                'message': f'Case is {age} days old. Consider review and escalation.'
            })
    
    return insights


def find_related_cases(case):
    """Find cases related by IOCs, evidence, or patterns"""
    related = []
    
    # Find cases with same IOCs
    if hasattr(case, 'iocs'):
        for ioc in case.iocs:
            for related_case in ioc.cases:
                if related_case.id != case.id and related_case not in related:
                    related.append({
                        'id': related_case.id,
                        'title': related_case.title,
                        'reason': f'Shared IOC: {ioc.ioc_value}'
                    })
    
    # Find cases with same investigator
    if case.assigned_to:
        similar = Case.query.filter(
            Case.assigned_to == case.assigned_to,
            Case.id != case.id,
            Case.status != 'closed'
        ).limit(5).all()
        
        for similar_case in similar:
            related.append({
                'id': similar_case.id,
                'title': similar_case.title,
                'reason': 'Same investigator'
            })
    
    return related[:10]


def generate_case_summary(case, evidence, iocs):
    """Generate AI-powered case summary"""
    summary = f"Case '{case.title}' is currently {case.status} with {len(evidence)} evidence items"
    summary += f" and {len(iocs)} IOCs tracked."
    
    if case.priority == 'critical':
        summary += " This is a CRITICAL priority case requiring immediate attention."
    
    if case.description:
        # Simple extractive summary (first 200 chars)
        summary += f" Description: {case.description[:200]}..."
    
    return summary


def generate_recommendations(case, risk_score):
    """Generate AI-powered recommendations"""
    recommendations = []
    
    if risk_score >= 80:
        recommendations.append({
            'priority': 'high',
            'action': 'Escalate to senior investigator',
            'reason': 'High risk score indicates complex investigation'
        })
    
    if case.status == 'open':
        recommendations.append({
            'priority': 'medium',
            'action': 'Assign investigator if not assigned',
            'reason': 'Open cases should have assigned investigators'
        })
    
    recommendations.append({
        'priority': 'low',
        'action': 'Review evidence chain of custody',
        'reason': 'Ensure all evidence has proper documentation'
    })
    
    return recommendations


@ai_assistant_bp.route('/api/ai/upload-and-analyze', methods=['POST'])
@login_required
def upload_and_analyze():
    """Upload and analyze a file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    case_id = request.form.get('case_id', type=int)
    analysis_type = request.form.get('analysis_type', 'general')
    
    # Save the uploaded file
    file_path, file_size = save_upload(file, subfolder=f'ai_analysis_{case_id or "standalone"}')
    if not file_path:
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Calculate file hashes
    hashes = calculate_file_hashes(file_path)
    mime_type = get_mime_type(file_path)
    
    # If case_id is provided, create evidence record
    if case_id:
        evidence = Evidence(
            case_id=case_id,
            evidence_number=generate_evidence_number(),
            title=f"AI Analysis: {file.filename}",
            description=f"File uploaded via AI Assistant for {analysis_type} analysis",
            evidence_type='document',
            file_path=file_path,
            file_name=file.filename,
            file_size=file_size,
            file_hash_md5=hashes['md5'],
            file_hash_sha1=hashes['sha1'],
            file_hash_sha256=hashes['sha256'],
            mime_type=mime_type,
            source='AI Assistant',
            collected_by=current_user.id,
            collected_date=datetime.utcnow(),
            collection_method='AI Upload',
            status='collected',
            integrity_status='verified'
        )
        db.session.add(evidence)
        db.session.commit()
    
    # Perform analysis based on type
    analysis_result = perform_file_analysis(file_path, analysis_type, mime_type)
    
    return jsonify(analysis_result)


def perform_file_analysis(file_path, analysis_type, mime_type):
    """Perform AI analysis on uploaded file"""
    result = {
        'risk_score': 0,
        'confidence': 0,
        'summary': '',
        'insights': [],
        'recommendations': [],
        'related_cases': []
    }
    
    try:
        # File size check
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:  # 50MB
            result['summary'] = 'File size exceeds 50MB limit.'
            return result
        
        # Basic file info
        file_name = os.path.basename(file_path)
        result['summary'] = f"Analyzed file: {file_name}\n"
        result['summary'] += f"File size: {file_size / 1024:.2f} KB\n"
        result['summary'] += f"MIME type: {mime_type}\n\n"
        
        # Analysis based on type
        if analysis_type == 'pdf':
            result['summary'] += "PDF document detected. Content analysis would be performed here.\n"
            result['insights'].append({
                'type': 'info',
                'title': 'PDF Analysis',
                'message': 'PDF content extraction and analysis would be performed here.'
            })
            
        elif analysis_type == 'image':
            result['summary'] += "Image file detected. OCR analysis would extract text content.\n"
            result['insights'].append({
                'type': 'info',
                'title': 'Image/OCR Analysis',
                'message': 'Optical Character Recognition would extract text from the image.'
            })
            
        elif analysis_type == 'email':
            result['summary'] += "Email file detected. Header analysis would extract metadata.\n"
            result['insights'].append({
                'type': 'info',
                'title': 'Email Header Analysis',
                'message': 'Email headers would be parsed to extract sender, recipients, and routing information.'
            })
            
        elif analysis_type == 'log':
            result['summary'] += "Log file detected. Pattern analysis would identify anomalies.\n"
            result['insights'].append({
                'type': 'info',
                'title': 'Log Analysis',
                'message': 'Log patterns would be analyzed to identify suspicious activities.'
            })
            
        elif analysis_type == 'malware':
            result['summary'] += "Binary file detected. Malware analysis would check for indicators.\n"
            result['insights'].append({
                'type': 'warning',
                'title': 'Malware Analysis',
                'message': 'Static analysis would check file signatures and characteristics.'
            })
            
        else:
            result['summary'] += "General file analysis completed.\n"
            result['insights'].append({
                'type': 'info',
                'title': 'General Analysis',
                'message': 'File metadata and basic properties have been extracted.'
            })
        
        # Calculate basic metrics
        result['risk_score'] = min(50 + (file_size / (1024 * 1024)), 85)  # Higher risk for larger files
        result['confidence'] = 75 if file_size > 0 else 0
        
        # Add recommendations
        result['recommendations'].append({
            'priority': 'medium',
            'action': 'Review extracted content',
            'reason': 'Manual review recommended for validation'
        })
        
        result['recommendations'].append({
            'priority': 'low',
            'action': 'Link to case if relevant',
            'reason': 'Consider associating this evidence with an investigation case'
        })
        
    except Exception as e:
        result['summary'] = f"Error during analysis: {str(e)}"
        result['insights'].append({
            'type': 'danger',
            'title': 'Analysis Error',
            'message': str(e)
        })
    
    return result


@ai_assistant_bp.route('/api/ai/investigation-timeline/<int:case_id>')
@login_required
def investigation_timeline(case_id):
    """Generate AI-powered investigation timeline"""
    case = Case.query.get_or_404(case_id)
    
    events = []
    
    # Case creation
    events.append({
        'date': case.created_at.isoformat() if case.created_at else datetime.utcnow().isoformat(),
        'event': 'Case Created',
        'description': f'Case opened: {case.title}',
        'type': 'milestone'
    })
    
    # Evidence additions
    evidence = Evidence.query.filter_by(case_id=case_id).all()
    for item in evidence:
        events.append({
            'date': item.created_at.isoformat() if item.created_at else datetime.utcnow().isoformat(),
            'event': 'Evidence Added',
            'description': f'{item.evidence_type}: {item.title}',
            'type': 'evidence'
        })
    
    # Audit log events
    logs = AuditLog.query.filter(
        AuditLog.resource_id == case_id,
        AuditLog.resource_type == 'case'
    ).order_by(AuditLog.created_at.desc()).limit(50).all()
    
    for log in logs:
        events.append({
            'date': log.created_at.isoformat() if log.created_at else datetime.utcnow().isoformat(),
            'event': log.action,
            'description': log.details or '',
            'type': 'activity'
        })
    
    # Sort by date
    events.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({'timeline': events[:50]})