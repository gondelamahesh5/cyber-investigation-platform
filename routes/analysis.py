import json
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.case import Case
from models.evidence import Evidence
from models.ioc import IOC
from models.summary import DocumentSummary
from models.entity import ExtractedEntity
from models.link import LinkAnalysis
from models.log_analysis import LogAnalysis
from models.email_header import EmailHeaderAnalysis
from models.ocr import OCRDocument
from models.pdf_intel import PDFIntelligence
from models.malware import MalwareAnalysis
from models.timeline import TimelineEvent
from services.audit_service import log_action
from services.file_service import save_upload, get_file_extension, format_file_size
from ai.entity_extraction import EntityExtractor
from ai.summarizer import TextSummarizer
from ai.link_analysis import LinkAnalyzer
from ai.log_analyzer import LogAnalyzer
from ai.email_analyzer import EmailHeaderAnalyzer
from ai.ocr_processor import OCRProcessor
from ai.pdf_analyzer import PDFAnalyzer
from ai.malware_analyzer import MalwareAnalyzer
from utils.helpers import sanitize_input

analysis_bp = Blueprint('analysis', __name__)

entity_extractor = EntityExtractor()
summarizer = TextSummarizer()
link_analyzer = LinkAnalyzer()
log_analyzer = LogAnalyzer()
email_analyzer = EmailHeaderAnalyzer()
ocr_processor = OCRProcessor()
pdf_analyzer = PDFAnalyzer()
malware_analyzer = MalwareAnalyzer()


@analysis_bp.route('/analysis')
@login_required
def index():
    cases = Case.query.all()
    summaries = DocumentSummary.query.order_by(DocumentSummary.created_at.desc()).limit(5).all()
    entities = ExtractedEntity.query.order_by(ExtractedEntity.created_at.desc()).limit(5).all()
    return render_template('analysis/index.html', cases=cases, summaries=summaries, entities=entities)


@analysis_bp.route('/analysis/summarize', methods=['GET', 'POST'])
@login_required
def summarize():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        text = sanitize_input(request.form.get('text', '').strip())
        document_name = sanitize_input(request.form.get('document_name', 'Manual text').strip())
        max_sentences = request.form.get('max_sentences', type=int, default=5)

        file = request.files.get('file')
        document_type = 'manual'

        if file and file.filename:
            file_path, file_size = save_upload(file, subfolder='summaries')
            if file_path:
                ext = get_file_extension(file_path)
                if ext == '.pdf':
                    doc_analyzer = PDFAnalyzer()
                    result = doc_analyzer.analyze(file_path)
                    text = result.get('extracted_text', '')
                    document_type = 'pdf'
                elif ext in ['.txt', '.csv']:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                    document_type = 'text'
                document_name = file.filename

        if not text:
            flash('No text provided for summarization', 'danger')
            return render_template('analysis/summarize.html', cases=Case.query.all())

        result = summarizer.summarize(text, max_sentences=max_sentences)
        language = summarizer.detect_language(text)
        sentiment = summarizer.detect_sentiment(text)
        keywords = summarizer.extract_keywords(text, top_n=10)

        summary = DocumentSummary(
            case_id=case_id,
            document_type=document_type,
            document_name=document_name,
            original_text=text[:50000],
            summary_text=result['summary'],
            summary_length=len(result['summary'].split()),
            compression_ratio=result['compression_ratio'],
            key_points='\n'.join(result['key_points']),
            sentiment=sentiment,
            language=language,
            model_used='extractive-summarizer-v1',
            created_by=current_user.id
        )
        db.session.add(summary)
        db.session.commit()

        log_action(current_user.id, 'summarize_document', 'summary', summary.id, f'Summarized document: {document_name}')
        flash('Document summarized successfully', 'success')
        return redirect(url_for('analysis.view_summary', summary_id=summary.id))

    return render_template('analysis/summarize.html', cases=Case.query.all())


@analysis_bp.route('/analysis/summaries')
@login_required
def list_summaries():
    page = request.args.get('page', 1, type=int)
    summaries = DocumentSummary.query.order_by(DocumentSummary.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('analysis/summaries.html', summaries=summaries)


@analysis_bp.route('/analysis/summaries/<int:summary_id>')
@login_required
def view_summary(summary_id):
    summary = DocumentSummary.query.get_or_404(summary_id)
    return render_template('analysis/view_summary.html', summary=summary)


@analysis_bp.route('/analysis/entities', methods=['GET', 'POST'])
@login_required
def extract_entities():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        text = sanitize_input(request.form.get('text', '').strip())
        file = request.files.get('file')

        if file and file.filename:
            file_path, file_size = save_upload(file, subfolder='entities')
            if file_path:
                ext = get_file_extension(file_path)
                if ext == '.pdf':
                    doc_analyzer = PDFAnalyzer()
                    result = doc_analyzer.analyze(file_path)
                    text = result.get('extracted_text', '')
                elif ext in ['.txt', '.csv']:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
                    ocr_result = ocr_processor.process_image(file_path)
                    text = ocr_result.get('extracted_text', '')

        if not text:
            flash('No text provided for entity extraction', 'danger')
            return render_template('analysis/entities.html', cases=Case.query.all())

        entities_with_context = entity_extractor.extract_with_context(text)
        entity_groups = entity_extractor.extract(text)

        created_count = 0
        entity_type_map = {
            'ipv4': 'IP Address', 'ipv6': 'IP Address', 'email': 'Email',
            'url': 'URL', 'domain': 'Domain', 'phone': 'Phone Number',
            'md5': 'File Hash', 'sha1': 'File Hash', 'sha256': 'File Hash',
            'cve': 'CVE', 'mac': 'MAC Address', 'file_path': 'File Path',
            'date': 'Date', 'bitcoin': 'Bitcoin Address', 'ethereum': 'Ethereum Address'
        }

        for entity in entities_with_context:
            if entity['type'] not in ['bitcoin', 'ethereum']:
                if created_count >= 200:
                    break
                extracted = ExtractedEntity(
                    case_id=case_id,
                    entity_type=entity_type_map.get(entity['type'], entity['type']),
                    entity_value=entity['value'][:500],
                    context=entity['context'][:1000],
                    confidence=0.95,
                    source_type='text_extraction',
                    created_by=current_user.id
                )
                db.session.add(extracted)
                created_count += 1

        db.session.commit()

        log_action(current_user.id, 'extract_entities', 'entity', case_id, f'Extracted {created_count} entities')
        flash(f'Extracted {created_count} entities', 'success')
        return redirect(url_for('analysis.list_entities'))

    return render_template('analysis/entities.html', cases=Case.query.all())


@analysis_bp.route('/analysis/entities/list')
@login_required
def list_entities():
    page = request.args.get('page', 1, type=int)
    case_id = request.args.get('case_id', type=int)
    entity_type = request.args.get('type', '')

    query = ExtractedEntity.query
    if case_id:
        query = query.filter(ExtractedEntity.case_id == case_id)
    if entity_type:
        query = query.filter(ExtractedEntity.entity_type == entity_type)

    entities = query.order_by(ExtractedEntity.created_at.desc()).paginate(page=page, per_page=25, error_out=False)
    return render_template('analysis/entity_list.html', entities=entities, case_id=case_id, entity_type=entity_type)


@analysis_bp.route('/analysis/link', methods=['GET', 'POST'])
@login_required
def link_analysis():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        analysis_name = sanitize_input(request.form.get('analysis_name', 'Link Analysis').strip())
        nodes_json = request.form.get('nodes', '[]')
        edges_json = request.form.get('edges', '[]')

        try:
            nodes = json.loads(nodes_json)
            edges = json.loads(edges_json)
        except json.JSONDecodeError:
            flash('Invalid graph data', 'danger')
            return render_template('analysis/link.html', cases=Case.query.all())

        nodes = [n for n in nodes if n.get('id')]
        edges = [e for e in edges if e.get('source') and e.get('target')]

        result = link_analyzer.analyze(nodes, edges)

        analysis = LinkAnalysis(
            case_id=case_id,
            analysis_name=analysis_name,
            description='Link/network analysis of case entities',
            graph_data=result['graph_data'],
            nodes_count=result['nodes_count'],
            edges_count=result['edges_count'],
            central_nodes=json.dumps(result['central_nodes']),
            communities=json.dumps(result['communities']),
            created_by=current_user.id
        )
        db.session.add(analysis)
        db.session.commit()

        log_action(current_user.id, 'link_analysis', 'link', analysis.id, f'Link analysis: {analysis_name}')
        flash('Link analysis completed', 'success')
        return redirect(url_for('analysis.view_link', link_id=analysis.id))

    return render_template('analysis/link.html', cases=Case.query.all())


@analysis_bp.route('/analysis/link/<int:link_id>')
@login_required
def view_link(link_id):
    analysis = LinkAnalysis.query.get_or_404(link_id)
    return render_template('analysis/view_link.html', analysis=analysis)


@analysis_bp.route('/analysis/logs', methods=['GET', 'POST'])
@login_required
def analyze_logs():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        log_type = request.form.get('log_type', 'generic')
        file = request.files.get('file')
        log_text = sanitize_input(request.form.get('log_text', ''))

        log_content = log_text
        file_name = 'manual input'

        if file and file.filename:
            file_path, file_size = save_upload(file, subfolder='logs')
            if file_path:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                file_name = file.filename

        if not log_content:
            flash('No log content provided', 'danger')
            return render_template('analysis/logs.html', cases=Case.query.all())

        result = log_analyzer.analyze(log_content, log_type)

        analysis = LogAnalysis(
            case_id=case_id,
            log_type=log_type,
            log_source='uploaded file' if file and file.filename else 'manual input',
            file_name=file_name,
            total_entries=result['total_entries'],
            suspicious_entries=result['suspicious_entries'],
            failed_logins=result['failed_logins'],
            successful_logins=result['successful_logins'],
            brute_force_attempts=result['brute_force_attempts'],
            sql_injection_attempts=result['sql_injection_attempts'],
            xss_attempts=result['xss_attempts'],
            port_scan_attempts=result['port_scan_attempts'],
            ip_addresses=result['ip_addresses'],
            user_agents=result['user_agents'],
            anomalies_found=result['anomalies_found'],
            patterns_detected=result['patterns_detected'],
            severity=result['severity'],
            analysis_results=json.dumps(result.get('suspicious_logs', [])),
            created_by=current_user.id
        )
        db.session.add(analysis)
        db.session.commit()

        log_action(current_user.id, 'log_analysis', 'log_analysis', analysis.id, f'Log analysis: {file_name}')
        flash('Log analysis completed', 'success')
        return redirect(url_for('analysis.view_logs', analysis_id=analysis.id))

    return render_template('analysis/logs.html', cases=Case.query.all())


@analysis_bp.route('/analysis/logs/<int:analysis_id>')
@login_required
def view_logs(analysis_id):
    analysis = LogAnalysis.query.get_or_404(analysis_id)
    return render_template('analysis/view_logs.html', analysis=analysis)


@analysis_bp.route('/analysis/email', methods=['GET', 'POST'])
@login_required
def analyze_email():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        file = request.files.get('file')
        header_text = request.form.get('header_text', '')

        email_content = header_text
        file_name = 'manual input'

        if file and file.filename:
            file_path, file_size = save_upload(file, subfolder='emails')
            if file_path:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    email_content = f.read()
                file_name = file.filename

        if not email_content:
            flash('No email header content provided', 'danger')
            return render_template('analysis/email.html', cases=Case.query.all())

        result = email_analyzer.analyze(email_content)

        analysis = EmailHeaderAnalysis(
            case_id=case_id,
            subject=result['subject'],
            sender_email=result['sender_email'],
            sender_name=result['sender_name'],
            recipient_email=result['recipient_email'],
            reply_to=result['reply_to'],
            date_sent=result['date_sent'],
            message_id=result['message_id'],
            received_chain=result['received_chain'],
            spf_result=result['spf_result'],
            dkim_result=result['dkim_result'],
            dmarc_result=result['dmarc_result'],
            x_headers=result['x_headers'],
            return_path=result['return_path'],
            envelope_from=result['envelope_from'],
            source_ip=result['source_ip'],
            source_hostname=result['source_hostname'],
            user_agent=result['user_agent'],
            is_suspicious=result['is_suspicious'],
            spoofing_detected=result['spoofing_detected'],
            phishing_indicators=result['phishing_indicators'],
            severity=result['severity'],
            analysis_notes=f'Analyzed from: {file_name}',
            created_by=current_user.id
        )
        db.session.add(analysis)
        db.session.commit()

        log_action(current_user.id, 'email_analysis', 'email_header', analysis.id, f'Email header analysis: {file_name}')
        flash('Email header analysis completed', 'success')
        return redirect(url_for('analysis.view_email', analysis_id=analysis.id))

    return render_template('analysis/email.html', cases=Case.query.all())


@analysis_bp.route('/analysis/email/<int:analysis_id>')
@login_required
def view_email(analysis_id):
    analysis = EmailHeaderAnalysis.query.get_or_404(analysis_id)
    return render_template('analysis/view_email.html', analysis=analysis)


@analysis_bp.route('/analysis/ocr', methods=['GET', 'POST'])
@login_required
def ocr():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        file = request.files.get('file')

        if not file or not file.filename:
            flash('Please select an image file', 'danger')
            return render_template('analysis/ocr.html', cases=Case.query.all())

        file_path, file_size = save_upload(file, subfolder='ocr')
        if not file_path:
            flash('File type not allowed', 'danger')
            return render_template('analysis/ocr.html', cases=Case.query.all())

        result = ocr_processor.process_image(file_path)

        entities = entity_extractor.extract(result['extracted_text'])

        ocr_doc = OCRDocument(
            case_id=case_id,
            file_name=file.filename,
            file_path=file_path,
            extracted_text=result['extracted_text'],
            confidence_score=result['confidence_score'],
            page_count=result['page_count'],
            entities_found=json.dumps(entities),
            status='processed',
            created_by=current_user.id
        )
        db.session.add(ocr_doc)
        db.session.commit()

        log_action(current_user.id, 'ocr_analysis', 'ocr', ocr_doc.id, f'OCR analysis: {file.filename}')
        flash('OCR analysis completed', 'success')
        return redirect(url_for('analysis.view_ocr', ocr_id=ocr_doc.id))

    return render_template('analysis/ocr.html', cases=Case.query.all())


@analysis_bp.route('/analysis/ocr/<int:ocr_id>')
@login_required
def view_ocr(ocr_id):
    ocr_doc = OCRDocument.query.get_or_404(ocr_id)
    entities = json.loads(ocr_doc.entities_found) if ocr_doc.entities_found else {}
    return render_template('analysis/view_ocr.html', ocr_doc=ocr_doc, entities=entities)


@analysis_bp.route('/analysis/pdf', methods=['GET', 'POST'])
@login_required
def pdf_intel():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        file = request.files.get('file')

        if not file or not file.filename:
            flash('Please select a PDF file', 'danger')
            return render_template('analysis/pdf.html', cases=Case.query.all())

        file_path, file_size = save_upload(file, subfolder='pdfs')
        if not file_path:
            flash('File type not allowed', 'danger')
            return render_template('analysis/pdf.html', cases=Case.query.all())

        result = pdf_analyzer.analyze(file_path)

        summary_result = None
        if result['extracted_text']:
            summary_result = summarizer.summarize(result['extracted_text'], max_sentences=3)

        pdf_doc = PDFIntelligence(
            case_id=case_id,
            file_name=file.filename,
            file_path=file_path,
            file_size=result['file_size'],
            page_count=result['page_count'],
            pdf_metadata=result['metadata'],
            extracted_text=result['extracted_text'],
            summary=summary_result['summary'] if summary_result else '',
            urls_found=result['urls_found'],
            emails_found=result['emails_found'],
            phone_numbers=result['phone_numbers'],
            dates_found=result['dates_found'],
            is_malicious=result['is_malicious'],
            javascript_detected=result['javascript_detected'],
            embedded_files=result['embedded_files'],
            suspicious_indicators=result['suspicious_indicators'],
            status='processed',
            created_by=current_user.id
        )
        db.session.add(pdf_doc)
        db.session.commit()

        log_action(current_user.id, 'pdf_analysis', 'pdf_intel', pdf_doc.id, f'PDF intelligence analysis: {file.filename}')
        flash('PDF intelligence analysis completed', 'success')
        return redirect(url_for('analysis.view_pdf', pdf_id=pdf_doc.id))

    return render_template('analysis/pdf.html', cases=Case.query.all())


@analysis_bp.route('/analysis/pdf/<int:pdf_id>')
@login_required
def view_pdf(pdf_id):
    pdf_doc = PDFIntelligence.query.get_or_404(pdf_id)
    return render_template('analysis/view_pdf.html', pdf_doc=pdf_doc)


@analysis_bp.route('/analysis/malware', methods=['GET', 'POST'])
@login_required
def malware():
    if request.method == 'POST':
        case_id = request.form.get('case_id', type=int)
        file = request.files.get('file')

        if not file or not file.filename:
            flash('Please select a file to analyze', 'danger')
            return render_template('analysis/malware.html', cases=Case.query.all())

        file_path, file_size = save_upload(file, subfolder='malware')
        if not file_path:
            flash('File type not allowed', 'danger')
            return render_template('analysis/malware.html', cases=Case.query.all())

        result = malware_analyzer.analyze(file_path)

        malware_analysis = MalwareAnalysis(
            case_id=case_id,
            file_name=file.filename,
            file_hash_md5=result['file_hash_md5'],
            file_hash_sha1=result['file_hash_sha1'],
            file_hash_sha256=result['file_hash_sha256'],
            file_size=result['file_size'],
            file_type=result['file_type'],
            malware_family=result['malware_family'],
            malware_type=result['malware_type'],
            severity=result['severity'],
            confidence=result['confidence'],
            detection_ratio=result['detection_ratio'],
            strings_found=result['strings_found'],
            urls_found=result['urls_found'],
            ips_found=result['ips_found'],
            static_analysis=result['suspicious_indicators'],
            status='analyzed',
            created_by=current_user.id
        )
        db.session.add(malware_analysis)
        db.session.commit()

        log_action(current_user.id, 'malware_analysis', 'malware', malware_analysis.id, f'Malware analysis: {file.filename}')
        flash('Malware analysis completed', 'success')
        return redirect(url_for('analysis.view_malware', malware_id=malware_analysis.id))

    return render_template('analysis/malware.html', cases=Case.query.all())


@analysis_bp.route('/analysis/malware/<int:malware_id>')
@login_required
def view_malware(malware_id):
    malware_analysis = MalwareAnalysis.query.get_or_404(malware_id)
    return render_template('analysis/view_malware.html', malware=malware_analysis)


@analysis_bp.route('/analysis/timeline/<int:case_id>')
@login_required
def timeline(case_id):
    case = Case.query.get_or_404(case_id)
    events = TimelineEvent.query.filter_by(case_id=case_id).order_by(TimelineEvent.event_date.asc()).all()
    return render_template('analysis/timeline.html', case=case, events=events)