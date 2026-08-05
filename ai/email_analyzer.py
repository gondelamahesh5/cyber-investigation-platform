import re
from datetime import datetime


class EmailHeaderAnalyzer:
    def __init__(self):
        self.header_patterns = {
            'subject': re.compile(r'^Subject:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'from': re.compile(r'^From:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'to': re.compile(r'^To:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'reply_to': re.compile(r'^Reply-To:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'date': re.compile(r'^Date:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'message_id': re.compile(r'^Message-ID:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'return_path': re.compile(r'^Return-Path:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'envelope_from': re.compile(r'^Envelope-From:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'received': re.compile(r'^Received:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'spf': re.compile(r'^Received-SPF:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'dkim': re.compile(r'^DKIM-Signature:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'dmarc': re.compile(r'^Authentication-Results:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'user_agent': re.compile(r'^User-Agent:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
            'x_headers': re.compile(r'^X-[\w-]+:\s*(.+)$', re.IGNORECASE | re.MULTILINE),
        }
        self.email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
        self.ip_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        self.phishing_keywords = [
            'urgent', 'verify', 'account', 'suspended', 'password', 'credit card',
            'bank', 'paypal', 'security', 'update', 'confirm', 'login', 'click here',
            'free', 'winner', 'prize', 'lottery', 'inheritance', 'wire transfer',
            'western union', 'money gram', 'gift card', 'bitcoin', 'cryptocurrency'
        ]

    def analyze(self, header_text):
        if not header_text:
            return self._empty_result()

        headers = {}
        for key, pattern in self.header_patterns.items():
            matches = pattern.findall(header_text)
            if matches:
                headers[key] = matches

        subject = self._get_first(headers.get('subject'))
        sender = self._get_first(headers.get('from'))
        recipient = self._get_first(headers.get('to'))
        reply_to = self._get_first(headers.get('reply_to'))
        date_str = self._get_first(headers.get('date'))
        message_id = self._get_first(headers.get('message_id'))
        return_path = self._get_first(headers.get('return_path'))
        envelope_from = self._get_first(headers.get('envelope_from'))
        received_chain = '\n'.join(headers.get('received', []))
        spf_result = self._get_first(headers.get('spf'))
        dkim_result = self._get_first(headers.get('dkim'))
        dmarc_result = self._get_first(headers.get('dmarc'))
        user_agent = self._get_first(headers.get('user_agent'))
        x_headers = '\n'.join(headers.get('x_headers', []))

        sender_email = self._extract_email(sender)
        recipient_email = self._extract_email(recipient)
        reply_to_email = self._extract_email(reply_to)
        return_path_email = self._extract_email(return_path)
        envelope_from_email = self._extract_email(envelope_from)

        source_ips = self.ip_pattern.findall(received_chain)
        source_ip = source_ips[-1] if source_ips else None

        source_hostname = None
        if received_chain:
            hostname_match = re.search(r'from\s+([\w.-]+)', received_chain, re.IGNORECASE)
            if hostname_match:
                source_hostname = hostname_match.group(1)

        date_sent = self._parse_date(date_str)

        spoofing_detected = False
        if sender_email and return_path_email and sender_email != return_path_email:
            spoofing_detected = True
        if sender_email and envelope_from_email and sender_email != envelope_from_email:
            spoofing_detected = True

        phishing_indicators = []
        if subject:
            subject_lower = subject.lower()
            for keyword in self.phishing_keywords:
                if keyword in subject_lower:
                    phishing_indicators.append(f'Phishing keyword in subject: {keyword}')

        if reply_to_email and sender_email and reply_to_email != sender_email:
            phishing_indicators.append('Reply-To address differs from sender')

        if spoofing_detected:
            phishing_indicators.append('Email spoofing detected')

        if spf_result and 'fail' in spf_result.lower():
            phishing_indicators.append('SPF check failed')
        if dmarc_result and 'fail' in dmarc_result.lower():
            phishing_indicators.append('DMARC check failed')

        is_suspicious = len(phishing_indicators) > 0 or spoofing_detected

        severity = 'low'
        if len(phishing_indicators) > 3:
            severity = 'critical'
        elif len(phishing_indicators) > 1:
            severity = 'high'
        elif len(phishing_indicators) > 0:
            severity = 'medium'

        return {
            'subject': subject,
            'sender_email': sender_email,
            'sender_name': self._extract_name(sender),
            'recipient_email': recipient_email,
            'reply_to': reply_to_email,
            'date_sent': date_sent,
            'message_id': message_id,
            'received_chain': received_chain,
            'spf_result': spf_result,
            'dkim_result': dkim_result,
            'dmarc_result': dmarc_result,
            'x_headers': x_headers,
            'return_path': return_path_email,
            'envelope_from': envelope_from_email,
            'source_ip': source_ip,
            'source_hostname': source_hostname,
            'user_agent': user_agent,
            'is_suspicious': is_suspicious,
            'spoofing_detected': spoofing_detected,
            'phishing_indicators': '\n'.join(phishing_indicators) if phishing_indicators else 'No phishing indicators detected',
            'severity': severity
        }

    def _get_first(self, values):
        if values:
            return values[0].strip()
        return None

    def _extract_email(self, text):
        if not text:
            return None
        match = self.email_pattern.search(text)
        return match.group() if match else None

    def _extract_name(self, text):
        if not text:
            return None
        match = re.match(r'^([^<]+)', text)
        if match:
            name = match.group(1).strip().strip('"')
            return name if name else None
        return None

    def _parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            try:
                return datetime.strptime(date_str.strip(), '%d %b %Y %H:%M:%S %z')
            except ValueError:
                return None

    def _empty_result(self):
        return {
            'subject': None,
            'sender_email': None,
            'sender_name': None,
            'recipient_email': None,
            'reply_to': None,
            'date_sent': None,
            'message_id': None,
            'received_chain': '',
            'spf_result': None,
            'dkim_result': None,
            'dmarc_result': None,
            'x_headers': '',
            'return_path': None,
            'envelope_from': None,
            'source_ip': None,
            'source_hostname': None,
            'user_agent': None,
            'is_suspicious': False,
            'spoofing_detected': False,
            'phishing_indicators': 'No email header content provided',
            'severity': 'low'
        }