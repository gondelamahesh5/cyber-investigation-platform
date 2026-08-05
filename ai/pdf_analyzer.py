import os
import re
import json
from PyPDF2 import PdfReader
from ai.entity_extraction import EntityExtractor


class PDFAnalyzer:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.suspicious_indicators = [
            'javascript', 'js', 'launch', 'openaction', 'embeddedfile',
            'acroform', 'xfa', 'richmedia', '3d', 'flash', 'submitform',
            'importdata', 'exportdata', 'gotor', 'uri', 'movie', 'sound'
        ]

    def analyze(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return self._empty_result()

        try:
            reader = PdfReader(file_path)
            page_count = len(reader.pages)
            file_size = os.path.getsize(file_path)

            metadata = {}
            if reader.metadata:
                for key, value in reader.metadata.items():
                    if value:
                        metadata[str(key).replace('/', '')] = str(value)

            extracted_text = ''
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + '\n'
                except Exception:
                    continue

            entities = self.entity_extractor.extract(extracted_text)

            urls_found = entities.get('url', [])
            emails_found = entities.get('email', [])
            phone_numbers = entities.get('phone', [])
            dates_found = entities.get('date', [])

            javascript_detected = False
            embedded_files = []
            suspicious_indicators = []

            for page in reader.pages:
                try:
                    if '/JS' in page or '/JavaScript' in page:
                        javascript_detected = True
                        suspicious_indicators.append('JavaScript detected in PDF')
                    if '/EmbeddedFile' in page:
                        embedded_files.append('Embedded file detected')
                        suspicious_indicators.append('Embedded file detected in PDF')
                    if '/Launch' in page:
                        suspicious_indicators.append('Launch action detected in PDF')
                    if '/OpenAction' in page:
                        suspicious_indicators.append('OpenAction detected in PDF')
                except Exception:
                    continue

            is_malicious = javascript_detected or len(embedded_files) > 0 or len(suspicious_indicators) > 0

            return {
                'file_name': os.path.basename(file_path),
                'file_size': file_size,
                'page_count': page_count,
                'metadata': json.dumps(metadata),
                'extracted_text': extracted_text.strip(),
                'urls_found': '\n'.join(urls_found) if urls_found else '',
                'emails_found': '\n'.join(emails_found) if emails_found else '',
                'phone_numbers': '\n'.join(phone_numbers) if phone_numbers else '',
                'dates_found': '\n'.join(dates_found) if dates_found else '',
                'is_malicious': is_malicious,
                'javascript_detected': javascript_detected,
                'embedded_files': '\n'.join(embedded_files) if embedded_files else '',
                'suspicious_indicators': '\n'.join(suspicious_indicators) if suspicious_indicators else 'No suspicious indicators detected',
                'status': 'processed'
            }
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path) if file_path else '',
                'file_size': 0,
                'page_count': 0,
                'metadata': '{}',
                'extracted_text': '',
                'urls_found': '',
                'emails_found': '',
                'phone_numbers': '',
                'dates_found': '',
                'is_malicious': False,
                'javascript_detected': False,
                'embedded_files': '',
                'suspicious_indicators': f'Error analyzing PDF: {str(e)}',
                'status': 'error'
            }

    def _empty_result(self):
        return {
            'file_name': '',
            'file_size': 0,
            'page_count': 0,
            'metadata': '{}',
            'extracted_text': '',
            'urls_found': '',
            'emails_found': '',
            'phone_numbers': '',
            'dates_found': '',
            'is_malicious': False,
            'javascript_detected': False,
            'embedded_files': '',
            'suspicious_indicators': 'No PDF provided',
            'status': 'no file'
        }