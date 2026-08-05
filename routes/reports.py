import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import Evidence
from models.ioc import IOC
from models.timeline import TimelineEvent
from models.report import Report
from services.audit_service import log_action
from services.report_service import (
    generate_pdf_report, generate_csv_report, generate_excel_report,
    generate_case_report, get_report_path
)
from utils.helpers import generate_report_number, sanitize_input

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def list_reports():
    page = request.args.get('page', 1, type=int)
    reports = Report.query.order_by(Report.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('reports/list.html', reports=reports)


@reports_bp.route('/reports/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        title = sanitize_input(request.form.get('title', '').strip())
        report_type = request.form.get('report_type', 'case_report')
        report_format = request.form.get('format', 'pdf')
        classification = request.form.get('classification', 'confidential')

        if not case_id or not title:
            flash('Case and title are required', 'danger')
            return render_template('reports/generate.html', cases=Case.query.all())

        case = Case.query.get_or_404(case_id)
        evidences = Evidence.query.filter_by(case_id=case_id).all()
        iocs = IOC.query.filter_by(case_id=case_id).all()
        timeline_events = TimelineEvent.query.filter_by(case_id=case_id).all()

        report = Report(
            case_id=case_id,
            report_number=generate_report_number(),
            title=title,
            report_type=report_type,
            format=report_format,
            classification=classification,
            generated_by=current_user.id,
            status='generated'
        )
        db.session.add(report)
        db.session.commit()

        sections = generate_case_report(case, evidences, iocs, timeline_events)

        try:
            base_path = get_report_path(report_type, case.case_number)

            if report_format == 'pdf':
                output_path = base_path + '.pdf'
                generate_pdf_report(title, sections, output_path)
                report.file_path = output_path
                report.format = 'pdf'
            elif report_format == 'csv':
                output_path = base_path + '.csv'
                headers = ['Name', 'Value']
                rows = []
                for section in sections:
                    rows.append([section.get('heading', ''), ''])
                    for item in section.get('content', []):
                        rows.append(['', item])
                generate_csv_report(headers, rows, output_path)
                report.file_path = output_path
                report.format = 'csv'
            elif report_format == 'excel':
                output_path = base_path + '.xlsx'
                headers = ['Section', 'Content']
                rows = []
                for section in sections:
                    for item in section.get('content', []):
                        rows.append([section.get('heading', ''), item])
                generate_excel_report('Case Report', headers, rows, output_path)
                report.file_path = output_path
                report.format = 'xlsx'

            db.session.commit()
        except Exception as e:
            flash(f'Report generation failed: {str(e)}', 'danger')
            return redirect(url_for('reports.generate'))

        log_action(current_user.id, 'generate_report', 'report', report.id, f'Generated report {report.report_number}')
        flash('Report generated successfully', 'success')
        return redirect(url_for('reports.view_report', report_id=report.id))

    return render_template('reports/generate.html', cases=Case.query.all())


@reports_bp.route('/reports/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('reports/view.html', report=report)


@reports_bp.route('/reports/<int:report_id>/download')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.file_path and os.path.exists(report.file_path):
        log_action(current_user.id, 'download_report', 'report', report.id, f'Downloaded report {report.report_number}')
        filename = f"{report.report_number}.{report.format}"
        return send_file(report.file_path, as_attachment=True, download_name=filename)
    flash('Report file not found', 'danger')
    return redirect(url_for('reports.view_report', report_id=report_id))


@reports_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    report_number = report.report_number
    file_path = report.file_path

    db.session.delete(report)
    db.session.commit()

    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    log_action(current_user.id, 'delete_report', 'report', report_id, f'Deleted report {report_number}')
    flash('Report deleted', 'success')
    return redirect(url_for('reports.list_reports'))