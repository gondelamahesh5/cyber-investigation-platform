import os
import csv
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from openpyxl import Workbook
from flask import current_app


def generate_pdf_report(title, sections, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=8
    )

    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC', body_style))
    story.append(Spacer(1, 0.2 * inch))

    for section in sections:
        story.append(Paragraph(section.get('heading', ''), heading_style))
        content = section.get('content', '')
        if isinstance(content, list):
            for item in content:
                story.append(Paragraph(f'• {item}', body_style))
        else:
            story.append(Paragraph(str(content), body_style))
        story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    return output_path


def generate_csv_report(headers, rows, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return output_path


def generate_excel_report(sheet_name, headers, rows, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    ws.append(headers)
    for row in rows:
        ws.append(row)

    wb.save(output_path)
    return output_path


def generate_case_report(case, evidences, iocs, timeline_events):
    sections = [
        {
            'heading': 'Case Overview',
            'content': [
                f'Case Number: {case.case_number}',
                f'Title: {case.title}',
                f'Status: {case.status}',
                f'Priority: {case.priority}',
                f'Classification: {case.classification}',
                f'Opened: {case.opened_date.strftime("%Y-%m-%d") if case.opened_date else "N/A"}',
                f'Description: {case.description or "N/A"}'
            ]
        },
        {
            'heading': 'Victim Information',
            'content': [
                f'Name: {case.victim_name or "N/A"}',
                f'Contact: {case.victim_contact or "N/A"}',
                f'Financial Loss: {case.currency} {case.financial_loss or 0}'
            ]
        },
        {
            'heading': 'Suspect Information',
            'content': [
                f'Name: {case.suspect_name or "N/A"}',
                f'Contact: {case.suspect_contact or "N/A"}'
            ]
        },
        {
            'heading': 'Evidence Summary',
            'content': [
                f'Total Evidence Items: {len(evidences)}',
                *[f'{e.evidence_number}: {e.title} ({e.evidence_type})' for e in evidences]
            ]
        },
        {
            'heading': 'Indicators of Compromise',
            'content': [
                f'Total IOCs: {len(iocs)}',
                *[f'{i.ioc_type}: {i.ioc_value} (Threat: {i.threat_level})' for i in iocs]
            ]
        },
        {
            'heading': 'Timeline',
            'content': [
                f'Total Events: {len(timeline_events)}',
                *[f'{t.event_date.strftime("%Y-%m-%d %H:%M")}: {t.event_title}' for t in timeline_events]
            ]
        }
    ]
    return sections


def get_report_path(report_type, case_number):
    report_folder = current_app.config['REPORT_FOLDER']
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{case_number}_{report_type}_{timestamp}"
    return os.path.join(report_folder, filename)