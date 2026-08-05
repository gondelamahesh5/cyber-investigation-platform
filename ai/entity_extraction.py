import re
import ipaddress
from urllib.parse import urlparse


class EntityExtractor:
    def __init__(self):
        self.patterns = {
            'ipv4': re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
            'ipv6': re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'url': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
            'domain': re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b'),
            'md5': re.compile(r'\b[a-fA-F0-9]{32}\b'),
            'sha1': re.compile(r'\b[a-fA-F0-9]{40}\b'),
            'sha256': re.compile(r'\b[a-fA-F0-9]{64}\b'),
            'cve': re.compile(r'\bCVE-\d{4}-\d{4,7}\b'),
            'mac': re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'),
            'file_path': re.compile(r'\b(?:[A-Za-z]:)?(?:[\\/][\w\-. ]+)+\b'),
            'date': re.compile(r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'),
            'bitcoin': re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
            'ethereum': re.compile(r'\b0x[a-fA-F0-9]{40}\b'),
        }

    def extract(self, text):
        if not text:
            return {}

        entities = {}
        for entity_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                unique_matches = list(set(matches))
                entities[entity_type] = unique_matches

        return entities

    def extract_with_context(self, text, context_window=50):
        if not text:
            return []

        results = []
        for entity_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end].replace('\n', ' ').strip()
                results.append({
                    'type': entity_type,
                    'value': match.group(),
                    'context': context,
                    'position': match.start()
                })

        results.sort(key=lambda x: x['position'])
        return results

    def validate_ip(self, ip_str):
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

    def is_private_ip(self, ip_str):
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            return False

    def extract_domain_from_url(self, url):
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None

    def extract_indicators(self, text):
        entities = self.extract(text)
        indicators = []

        for entity_type, values in entities.items():
            for value in values:
                indicator = {
                    'type': entity_type,
                    'value': value,
                    'threat_level': 'unknown'
                }

                if entity_type in ('ipv4', 'ipv6'):
                    if self.is_private_ip(value):
                        indicator['threat_level'] = 'low'
                    else:
                        indicator['threat_level'] = 'medium'

                if entity_type in ('md5', 'sha1', 'sha256'):
                    indicator['threat_level'] = 'high'

                if entity_type == 'cve':
                    indicator['threat_level'] = 'high'

                indicators.append(indicator)

        return indicators