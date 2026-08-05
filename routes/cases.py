from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import Evidence
from models.ioc import IOC
from models.timeline import TimelineEvent
from models.user import User
from services.audit_service import log_action
from services.notification_service import create_notification
from utils.helpers import generate_case_number, sanitize_input, parse_tags

cases_bp = Blueprint('cases', __name__)


@cases_bp.route('/cases')
@login_required
def list_cases():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    search = request.args.get('search', '')

    query = Case.query
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if search:
        query = query.filter(
            (Case.title.ilike(f'%{search}%')) |
            (Case.case_number.ilike(f'%{search}%')) |
            (Case.description.ilike(f'%{search}%'))
        )

    cases = query.order_by(Case.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('cases/list.html', cases=cases, status=status, priority=priority, search=search)


@cases_bp.route('/cases/new', methods=['GET', 'POST'])
@login_required
def new_case():
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', '').strip())
        description = sanitize_input(request.form.get('description', '').strip())
        case_type = sanitize_input(request.form.get('case_type', '').strip())
        priority = request.form.get('priority', 'medium')
        classification = sanitize_input(request.form.get('classification', '').strip())
        severity = request.form.get('severity', 'low')
        assigned_to = request.form.get('assigned_to', type=int)
        location = sanitize_input(request.form.get('location', '').strip())
        jurisdiction = sanitize_input(request.form.get('jurisdiction', '').strip())
        victim_name = sanitize_input(request.form.get('victim_name', '').strip())
        victim_contact = sanitize_input(request.form.get('victim_contact', '').strip())
        suspect_name = sanitize_input(request.form.get('suspect_name', '').strip())
        suspect_contact = sanitize_input(request.form.get('suspect_contact', '').strip())
        financial_loss = request.form.get('financial_loss', type=float, default=0)
        currency = request.form.get('currency', 'USD')
        tags = request.form.get('tags', '').strip()
        due_date = request.form.get('due_date', '')

        if not title:
            flash('Case title is required', 'danger')
            return render_template('cases/new.html')

        case = Case(
            case_number=generate_case_number(),
            title=title,
            description=description,
            case_type=case_type,
            priority=priority,
            classification=classification,
            severity=severity,
            created_by=current_user.id,
            assigned_to=assigned_to,
            location=location,
            jurisdiction=jurisdiction,
            victim_name=victim_name,
            victim_contact=victim_contact,
            suspect_name=suspect_name,
            suspect_contact=suspect_contact,
            financial_loss=financial_loss,
            currency=currency,
            tags=tags,
            status='open'
        )

        if due_date:
            try:
                case.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                pass

        db.session.add(case)
        db.session.commit()

        if assigned_to:
            create_notification(
                assigned_to,
                'New Case Assigned',
                f'Case {case.case_number}: {case.title} has been assigned to you.',
                'case',
                'info',
                url_for('cases.view_case', case_id=case.id)
            )

        log_action(current_user.id, 'create_case', 'case', case.id, f'Created case {case.case_number}')
        flash('Case created successfully', 'success')
        return redirect(url_for('cases.view_case', case_id=case.id))

    users = User.query.filter_by(is_active=True).all()
    return render_template('cases/new.html', users=users)


@cases_bp.route('/cases/<int:case_id>')
@login_required
def view_case(case_id):
    case = Case.query.get_or_404(case_id)
    evidences = Evidence.query.filter_by(case_id=case_id).all()
    iocs = IOC.query.filter_by(case_id=case_id).all()
    timeline_events = TimelineEvent.query.filter_by(case_id=case_id).order_by(TimelineEvent.event_date.desc()).all()
    users = User.query.filter_by(is_active=True).all()
    return render_template(
        'cases/view.html',
        case=case,
        evidences=evidences,
        iocs=iocs,
        timeline_events=timeline_events,
        users=users
    )


@cases_bp.route('/cases/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_case(case_id):
    case = Case.query.get_or_404(case_id)

    if request.method == 'POST':
        case.title = sanitize_input(request.form.get('title', case.title).strip())
        case.description = sanitize_input(request.form.get('description', case.description).strip())
        case.case_type = sanitize_input(request.form.get('case_type', case.case_type).strip())
        case.priority = request.form.get('priority', case.priority)
        case.classification = sanitize_input(request.form.get('classification', case.classification).strip())
        case.severity = request.form.get('severity', case.severity)
        case.assigned_to = request.form.get('assigned_to', type=int)
        case.location = sanitize_input(request.form.get('location', case.location).strip())
        case.jurisdiction = sanitize_input(request.form.get('jurisdiction', case.jurisdiction).strip())
        case.victim_name = sanitize_input(request.form.get('victim_name', case.victim_name).strip())
        case.victim_contact = sanitize_input(request.form.get('victim_contact', case.victim_contact).strip())
        case.suspect_name = sanitize_input(request.form.get('suspect_name', case.suspect_name).strip())
        case.suspect_contact = sanitize_input(request.form.get('suspect_contact', case.suspect_contact).strip())
        case.financial_loss = request.form.get('financial_loss', type=float, default=case.financial_loss)
        case.currency = request.form.get('currency', case.currency)
        case.tags = request.form.get('tags', case.tags).strip()

        due_date = request.form.get('due_date', '')
        if due_date:
            try:
                case.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                pass

        db.session.commit()
        log_action(current_user.id, 'update_case', 'case', case.id, f'Updated case {case.case_number}')
        flash('Case updated successfully', 'success')
        return redirect(url_for('cases.view_case', case_id=case.id))

    users = User.query.filter_by(is_active=True).all()
    return render_template('cases/edit.html', case=case, users=users)


@cases_bp.route('/cases/<int:case_id>/status', methods=['POST'])
@login_required
def update_status(case_id):
    case = Case.query.get_or_404(case_id)
    new_status = request.form.get('status', '')

    valid_statuses = ['open', 'under_investigation', 'pending', 'closed']
    if new_status not in valid_statuses:
        flash('Invalid status', 'danger')
        return redirect(url_for('cases.view_case', case_id=case_id))

    case.status = new_status
    if new_status == 'closed':
        case.closed_date = datetime.utcnow()
    else:
        case.closed_date = None

    db.session.commit()
    log_action(current_user.id, 'update_case_status', 'case', case.id, f'Changed status to {new_status}')
    flash('Case status updated', 'success')
    return redirect(url_for('cases.view_case', case_id=case_id))


@cases_bp.route('/cases/<int:case_id>/delete', methods=['POST'])
@login_required
def delete_case(case_id):
    case = Case.query.get_or_404(case_id)
    case_number = case.case_number
    db.session.delete(case)
    db.session.commit()
    log_action(current_user.id, 'delete_case', 'case', case_id, f'Deleted case {case_number}')
    flash('Case deleted', 'success')
    return redirect(url_for('cases.list_cases'))


@cases_bp.route('/cases/<int:case_id>/timeline', methods=['POST'])
@login_required
def add_timeline_event(case_id):
    case = Case.query.get_or_404(case_id)
    event_title = sanitize_input(request.form.get('event_title', '').strip())
    event_description = sanitize_input(request.form.get('event_description', '').strip())
    event_date = request.form.get('event_date', '')
    event_type = sanitize_input(request.form.get('event_type', '').strip())
    importance = request.form.get('importance', 'normal')

    if not event_title:
        flash('Event title is required', 'danger')
        return redirect(url_for('cases.view_case', case_id=case_id))

    event = TimelineEvent(
        case_id=case_id,
        event_title=event_title,
        event_description=event_description,
        event_type=event_type,
        importance=importance,
        created_by=current_user.id
    )

    if event_date:
        try:
            event.event_date = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                event.event_date = datetime.strptime(event_date, '%Y-%m-%d')
            except ValueError:
                event.event_date = datetime.utcnow()
    else:
        event.event_date = datetime.utcnow()

    db.session.add(event)
    db.session.commit()
    log_action(current_user.id, 'add_timeline_event', 'case', case_id, f'Added timeline event: {event_title}')
    flash('Timeline event added', 'success')
    return redirect(url_for('cases.view_case', case_id=case_id))