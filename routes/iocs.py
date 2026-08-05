from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.ioc import IOC
from models.case import Case
from services.audit_service import log_action
from utils.helpers import sanitize_input

iocs_bp = Blueprint('iocs', __name__)


@iocs_bp.route('/iocs')
@login_required
def list_iocs():
    page = request.args.get('page', 1, type=int)
    ioc_type = request.args.get('type', '')
    threat_level = request.args.get('threat_level', '')
    search = request.args.get('search', '')

    query = IOC.query
    if ioc_type:
        query = query.filter(IOC.ioc_type == ioc_type)
    if threat_level:
        query = query.filter(IOC.threat_level == threat_level)
    if search:
        query = query.filter(
            (IOC.ioc_value.ilike(f'%{search}%')) |
            (IOC.description.ilike(f'%{search}%'))
        )

    iocs = query.order_by(IOC.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('iocs/list.html', iocs=iocs, ioc_type=ioc_type, threat_level=threat_level, search=search)


@iocs_bp.route('/iocs/new', methods=['GET', 'POST'])
@login_required
def new_ioc():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        ioc_type = request.form.get('ioc_type', '')
        ioc_value = sanitize_input(request.form.get('ioc_value', '').strip())
        description = sanitize_input(request.form.get('description', '').strip())
        threat_level = request.form.get('threat_level', 'medium')
        confidence = request.form.get('confidence', type=int, default=50)
        source = sanitize_input(request.form.get('source', '').strip())
        tags = request.form.get('tags', '').strip()
        tlp_level = request.form.get('tlp_level', 'amber')

        if not ioc_type or not ioc_value:
            flash('IOC type and value are required', 'danger')
            return render_template('iocs/new.html')

        ioc = IOC(
            case_id=case_id,
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            description=description,
            threat_level=threat_level,
            confidence=confidence,
            source=source,
            tags=tags,
            tlp_level=tlp_level,
            created_by=current_user.id,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )

        db.session.add(ioc)
        db.session.commit()

        log_action(current_user.id, 'create_ioc', 'ioc', ioc.id, f'Created IOC {ioc_type}: {ioc_value}')
        flash('IOC created successfully', 'success')
        return redirect(url_for('iocs.view_ioc', ioc_id=ioc.id))

    cases = Case.query.all()
    return render_template('iocs/new.html', cases=cases)


@iocs_bp.route('/iocs/<int:ioc_id>')
@login_required
def view_ioc(ioc_id):
    ioc = IOC.query.get_or_404(ioc_id)
    return render_template('iocs/view.html', ioc=ioc)


@iocs_bp.route('/iocs/<int:ioc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ioc(ioc_id):
    ioc = IOC.query.get_or_404(ioc_id)

    if request.method == 'POST':
        ioc.ioc_type = request.form.get('ioc_type', ioc.ioc_type)
        ioc.ioc_value = sanitize_input(request.form.get('ioc_value', ioc.ioc_value).strip())
        ioc.description = sanitize_input(request.form.get('description', ioc.description).strip())
        ioc.threat_level = request.form.get('threat_level', ioc.threat_level)
        ioc.confidence = request.form.get('confidence', type=int, default=ioc.confidence)
        ioc.source = sanitize_input(request.form.get('source', ioc.source).strip())
        ioc.tags = request.form.get('tags', ioc.tags).strip()
        ioc.tlp_level = request.form.get('tlp_level', ioc.tlp_level)
        ioc.status = request.form.get('status', ioc.status)

        db.session.commit()
        log_action(current_user.id, 'update_ioc', 'ioc', ioc.id, f'Updated IOC {ioc.ioc_value}')
        flash('IOC updated successfully', 'success')
        return redirect(url_for('iocs.view_ioc', ioc_id=ioc.id))

    return render_template('iocs/edit.html', ioc=ioc)


@iocs_bp.route('/iocs/<int:ioc_id>/delete', methods=['POST'])
@login_required
def delete_ioc(ioc_id):
    ioc = IOC.query.get_or_404(ioc_id)
    ioc_value = ioc.ioc_value
    db.session.delete(ioc)
    db.session.commit()
    log_action(current_user.id, 'delete_ioc', 'ioc', ioc_id, f'Deleted IOC {ioc_value}')
    flash('IOC deleted', 'success')
    return redirect(url_for('iocs.list_iocs'))


@iocs_bp.route('/iocs/check', methods=['POST'])
@login_required
def check_ioc():
    value = request.form.get('value', '').strip()
    if not value:
        return jsonify({'error': 'No value provided'}), 400

    ioc = IOC.query.filter_by(ioc_value=value).first()
    if ioc:
        return jsonify({
            'found': True,
            'ioc': ioc.to_dict()
        })
    return jsonify({'found': False})