from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.threat import ThreatIntel
from services.audit_service import log_action
from utils.helpers import sanitize_input

threats_bp = Blueprint('threats', __name__)


@threats_bp.route('/threats')
@login_required
def list_threats():
    page = request.args.get('page', 1, type=int)
    threat_type = request.args.get('type', '')
    severity = request.args.get('severity', '')
    search = request.args.get('search', '')

    query = ThreatIntel.query
    if threat_type:
        query = query.filter(ThreatIntel.threat_type == threat_type)
    if severity:
        query = query.filter(ThreatIntel.severity == severity)
    if search:
        query = query.filter(
            (ThreatIntel.title.ilike(f'%{search}%')) |
            (ThreatIntel.description.ilike(f'%{search}%'))
        )

    threats = query.order_by(ThreatIntel.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('threats/list.html', threats=threats, threat_type=threat_type, severity=severity, search=search)


@threats_bp.route('/threats/new', methods=['GET', 'POST'])
@login_required
def new_threat():
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', '').strip())
        description = sanitize_input(request.form.get('description', '').strip())
        threat_type = request.form.get('threat_type', '')
        severity = request.form.get('severity', 'medium')
        confidence = request.form.get('confidence', type=int, default=50)
        source = sanitize_input(request.form.get('source', '').strip())
        source_url = sanitize_input(request.form.get('source_url', '').strip())
        affected_platforms = sanitize_input(request.form.get('affected_platforms', '').strip())
        attack_vector = sanitize_input(request.form.get('attack_vector', '').strip())
        impact = sanitize_input(request.form.get('impact', '').strip())
        mitigation = sanitize_input(request.form.get('mitigation', '').strip())
        indicators = sanitize_input(request.form.get('indicators', '').strip())
        tags = request.form.get('tags', '').strip()
        tlp_level = request.form.get('tlp_level', 'amber')

        if not title:
            flash('Threat title is required', 'danger')
            return render_template('threats/new.html')

        threat = ThreatIntel(
            title=title,
            description=description,
            threat_type=threat_type,
            severity=severity,
            confidence=confidence,
            source=source,
            source_url=source_url,
            affected_platforms=affected_platforms,
            attack_vector=attack_vector,
            impact=impact,
            mitigation=mitigation,
            indicators=indicators,
            tags=tags,
            tlp_level=tlp_level,
            created_by=current_user.id,
            published_date=datetime.utcnow(),
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )

        db.session.add(threat)
        db.session.commit()

        log_action(current_user.id, 'create_threat', 'threat', threat.id, f'Created threat intel: {title}')
        flash('Threat intelligence created successfully', 'success')
        return redirect(url_for('threats.view_threat', threat_id=threat.id))

    return render_template('threats/new.html')


@threats_bp.route('/threats/<int:threat_id>')
@login_required
def view_threat(threat_id):
    threat = ThreatIntel.query.get_or_404(threat_id)
    return render_template('threats/view.html', threat=threat)


@threats_bp.route('/threats/<int:threat_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_threat(threat_id):
    threat = ThreatIntel.query.get_or_404(threat_id)

    if request.method == 'POST':
        threat.title = sanitize_input(request.form.get('title', threat.title).strip())
        threat.description = sanitize_input(request.form.get('description', threat.description).strip())
        threat.threat_type = request.form.get('threat_type', threat.threat_type)
        threat.severity = request.form.get('severity', threat.severity)
        threat.confidence = request.form.get('confidence', type=int, default=threat.confidence)
        threat.source = sanitize_input(request.form.get('source', threat.source).strip())
        threat.source_url = sanitize_input(request.form.get('source_url', threat.source_url).strip())
        threat.affected_platforms = sanitize_input(request.form.get('affected_platforms', threat.affected_platforms).strip())
        threat.attack_vector = sanitize_input(request.form.get('attack_vector', threat.attack_vector).strip())
        threat.impact = sanitize_input(request.form.get('impact', threat.impact).strip())
        threat.mitigation = sanitize_input(request.form.get('mitigation', threat.mitigation).strip())
        threat.indicators = sanitize_input(request.form.get('indicators', threat.indicators).strip())
        threat.tags = request.form.get('tags', threat.tags).strip()
        threat.tlp_level = request.form.get('tlp_level', threat.tlp_level)
        threat.status = request.form.get('status', threat.status)

        db.session.commit()
        log_action(current_user.id, 'update_threat', 'threat', threat.id, f'Updated threat intel: {threat.title}')
        flash('Threat intelligence updated successfully', 'success')
        return redirect(url_for('threats.view_threat', threat_id=threat.id))

    return render_template('threats/edit.html', threat=threat)


@threats_bp.route('/threats/<int:threat_id>/delete', methods=['POST'])
@login_required
def delete_threat(threat_id):
    threat = ThreatIntel.query.get_or_404(threat_id)
    title = threat.title
    db.session.delete(threat)
    db.session.commit()
    log_action(current_user.id, 'delete_threat', 'threat', threat_id, f'Deleted threat intel: {title}')
    flash('Threat intelligence deleted', 'success')
    return redirect(url_for('threats.list_threats'))