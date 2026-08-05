from datetime import datetime
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from extensions import db
from models.evidence import Evidence
from models.case import Case
from services.audit_service import log_action
from services.file_service import save_upload, calculate_file_hashes, get_mime_type, delete_file, format_file_size
from utils.helpers import generate_evidence_number, sanitize_input

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('/evidence')
@login_required
def list_evidence():
    page = request.args.get('page', 1, type=int)
    case_id = request.args.get('case_id', type=int)
    evidence_type = request.args.get('type', '')
    search = request.args.get('search', '')

    query = Evidence.query
    if case_id:
        query = query.filter(Evidence.case_id == case_id)
    if evidence_type:
        query = query.filter(Evidence.evidence_type == evidence_type)
    if search:
        query = query.filter(
            (Evidence.title.ilike(f'%{search}%')) |
            (Evidence.evidence_number.ilike(f'%{search}%')) |
            (Evidence.file_name.ilike(f'%{search}%'))
        )

    evidence = query.order_by(Evidence.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    cases = Case.query.all()
    return render_template('evidence/list.html', evidence=evidence, cases=cases, case_id=case_id, evidence_type=evidence_type, search=search)


@evidence_bp.route('/evidence/upload', methods=['GET', 'POST'])
@login_required
def upload_evidence():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        title = sanitize_input(request.form.get('title', '').strip())
        description = sanitize_input(request.form.get('description', '').strip())
        evidence_type = request.form.get('evidence_type', '')
        source = sanitize_input(request.form.get('source', '').strip())
        collection_method = sanitize_input(request.form.get('collection_method', '').strip())
        file = request.files.get('file')

        if not case_id or not title or not evidence_type:
            flash('Case, title, and evidence type are required', 'danger')
            return render_template('evidence/upload.html')

        if not file or not file.filename:
            flash('Please select a file to upload', 'danger')
            return render_template('evidence/upload.html')

        file_path, file_size = save_upload(file, subfolder=f'case_{case_id}')
        if not file_path:
            flash('File type not allowed', 'danger')
            return render_template('evidence/upload.html')

        hashes = calculate_file_hashes(file_path)
        mime_type = get_mime_type(file_path)

        evidence = Evidence(
            case_id=case_id,
            evidence_number=generate_evidence_number(),
            title=title,
            description=description,
            evidence_type=evidence_type,
            file_path=file_path,
            file_name=file.filename,
            file_size=file_size,
            file_hash_md5=hashes['md5'],
            file_hash_sha1=hashes['sha1'],
            file_hash_sha256=hashes['sha256'],
            mime_type=mime_type,
            source=source,
            collected_by=current_user.id,
            collected_date=datetime.utcnow(),
            collection_method=collection_method,
            status='collected',
            integrity_status='verified'
        )

        db.session.add(evidence)
        db.session.commit()

        log_action(current_user.id, 'upload_evidence', 'evidence', evidence.id, f'Uploaded evidence {evidence.evidence_number}')
        flash('Evidence uploaded successfully', 'success')
        return redirect(url_for('evidence.view_evidence', evidence_id=evidence.id))

    cases = Case.query.filter(Case.status != 'closed').all()
    return render_template('evidence/upload.html', cases=cases)


@evidence_bp.route('/evidence/<int:evidence_id>')
@login_required
def view_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    return render_template('evidence/view.html', evidence=evidence)


@evidence_bp.route('/evidence/<int:evidence_id>/download')
@login_required
def download_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    if evidence.file_path and os.path.exists(evidence.file_path):
        log_action(current_user.id, 'download_evidence', 'evidence', evidence.id, f'Downloaded evidence {evidence.evidence_number}')
        return send_file(evidence.file_path, as_attachment=True, download_name=evidence.file_name)
    flash('File not found', 'danger')
    return redirect(url_for('evidence.view_evidence', evidence_id=evidence_id))


@evidence_bp.route('/evidence/<int:evidence_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)

    if request.method == 'POST':
        evidence.title = sanitize_input(request.form.get('title', evidence.title).strip())
        evidence.description = sanitize_input(request.form.get('description', evidence.description).strip())
        evidence.evidence_type = request.form.get('evidence_type', evidence.evidence_type)
        evidence.source = sanitize_input(request.form.get('source', evidence.source).strip())
        evidence.collection_method = sanitize_input(request.form.get('collection_method', evidence.collection_method).strip())
        evidence.status = request.form.get('status', evidence.status)
        evidence.notes = sanitize_input(request.form.get('notes', evidence.notes).strip())

        db.session.commit()
        log_action(current_user.id, 'update_evidence', 'evidence', evidence.id, f'Updated evidence {evidence.evidence_number}')
        flash('Evidence updated successfully', 'success')
        return redirect(url_for('evidence.view_evidence', evidence_id=evidence_id))

    return render_template('evidence/edit.html', evidence=evidence)


@evidence_bp.route('/evidence/<int:evidence_id>/delete', methods=['POST'])
@login_required
def delete_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    evidence_number = evidence.evidence_number
    file_path = evidence.file_path

    db.session.delete(evidence)
    db.session.commit()

    if file_path:
        delete_file(file_path)

    log_action(current_user.id, 'delete_evidence', 'evidence', evidence_id, f'Deleted evidence {evidence_number}')
    flash('Evidence deleted', 'success')
    return redirect(url_for('evidence.list_evidence'))