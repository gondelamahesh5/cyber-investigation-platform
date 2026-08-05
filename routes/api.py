from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import Evidence
from models.ioc import IOC
from models.threat import ThreatIntel
from models.user import User
from models.search import SearchIndex
from models.summary import DocumentSummary
from models.entity import ExtractedEntity
from services.audit_service import log_action
from ai.entity_extraction import EntityExtractor
from ai.summarizer import TextSummarizer

api_bp = Blueprint('api', __name__)

entity_extractor = EntityExtractor()
summarizer = TextSummarizer()


@api_bp.route('/health')
def health():
    from datetime import datetime
    db_status = 'ok'
    try:
        User.query.first()
    except Exception as e:
        db.session.rollback()
        db_status = 'error'
    return jsonify({
        'status': 'ok',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    return jsonify({
        'total_cases': Case.query.count(),
        'open_cases': Case.query.filter_by(status='open').count(),
        'total_evidence': Evidence.query.count(),
        'total_iocs': IOC.query.count(),
        'total_threats': ThreatIntel.query.count()
    })


@api_bp.route('/cases')
@login_required
def api_cases():
    cases = Case.query.all()
    return jsonify([case.to_dict() for case in cases])


@api_bp.route('/cases/<int:case_id>')
@login_required
def api_case(case_id):
    case = Case.query.get_or_404(case_id)
    return jsonify(case.to_dict())


@api_bp.route('/evidence')
@login_required
def api_evidence():
    case_id = request.args.get('case_id', type=int)
    query = Evidence.query
    if case_id:
        query = query.filter(Evidence.case_id == case_id)
    evidence = query.order_by(Evidence.created_at.desc()).limit(100).all()
    return jsonify([e.to_dict() for e in evidence])


@api_bp.route('/iocs')
@login_required
def api_iocs():
    iocs = IOC.query.order_by(IOC.created_at.desc()).limit(100).all()
    return jsonify([i.to_dict() for i in iocs])


@api_bp.route('/threats')
@login_required
def api_threats():
    threats = ThreatIntel.query.order_by(ThreatIntel.created_at.desc()).limit(100).all()
    return jsonify([t.to_dict() for t in threats])


@api_bp.route('/iocs/lookup', methods=['GET'])
@login_required
def ioc_lookup():
    value = request.args.get('value', '')
    if not value:
        return jsonify({'error': 'value parameter is required'}), 400

    ioc = IOC.query.filter_by(ioc_value=value).first()
    if ioc:
        return jsonify({'found': True, 'ioc': ioc.to_dict()})
    return jsonify({'found': False})


@api_bp.route('/entities/extract', methods=['POST'])
@login_required
def extract_entities():
    data = request.get_json()
    text = data.get('text', '') if data else ''

    if not text:
        return jsonify({'error': 'text is required'}), 400

    entities = entity_extractor.extract(text)
    indicators = entity_extractor.extract_indicators(text)

    return jsonify({
        'entities': entities,
        'indicators': indicators
    })


@api_bp.route('/summarize', methods=['POST'])
@login_required
def api_summarize():
    data = request.get_json()
    text = data.get('text', '') if data else ''
    max_sentences = data.get('max_sentences', 5) if data else 5

    if not text:
        return jsonify({'error': 'text is required'}), 400

    result = summarizer.summarize(text, max_sentences=max_sentences)
    keywords = summarizer.extract_keywords(text)
    sentiment = summarizer.detect_sentiment(text)
    language = summarizer.detect_language(text)

    return jsonify({
        'summary': result['summary'],
        'key_points': result['key_points'],
        'compression_ratio': result['compression_ratio'],
        'keywords': keywords,
        'sentiment': sentiment,
        'language': language
    })


@api_bp.route('/search')
@login_required
def api_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'results': []})

    results = []

    cases = Case.query.filter(
        (Case.title.ilike(f'%{q}%')) |
        (Case.case_number.ilike(f'%{q}%')) |
        (Case.tags.ilike(f'%{q}%'))
    ).limit(10).all()
    for case in cases:
        results.append({'type': 'case', 'id': case.id, 'title': case.case_number, 'subtitle': case.title})

    iocs = IOC.query.filter(
        (IOC.ioc_value.ilike(f'%{q}%')) |
        (IOC.description.ilike(f'%{q}%'))
    ).limit(10).all()
    for ioc in iocs:
        results.append({'type': 'ioc', 'id': ioc.id, 'title': ioc.ioc_value, 'subtitle': f'{ioc.ioc_type} - {ioc.threat_level}'})

    threats = ThreatIntel.query.filter(
        (ThreatIntel.title.ilike(f'%{q}%')) |
        (ThreatIntel.description.ilike(f'%{q}%'))
    ).limit(10).all()
    for threat in threats:
        results.append({'type': 'threat', 'id': threat.id, 'title': threat.title, 'subtitle': threat.severity})

    users = User.query.filter(
        (User.username.ilike(f'%{q}%')) |
        (User.full_name.ilike(f'%{q}%'))
    ).limit(5).all()
    for user in users:
        results.append({'type': 'user', 'id': user.id, 'title': user.username, 'subtitle': user.full_name})

    return jsonify({'results': results})