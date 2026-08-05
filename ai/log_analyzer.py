import re
from collections import Counter


class LogAnalyzer:
    def __init__(self):
        self.ip_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        self.user_agent_pattern = re.compile(r'User-Agent:\s*([^\r\n]+)', re.IGNORECASE)
        self.timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}')
        self.sql_injection_patterns = [
            re.compile(r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b.*['\"])", re.IGNORECASE),
            re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
            re.compile(r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b.*['\"])", re.IGNORECASE),
            re.compile(r"(\bOR\b\s+\d+\s*=\s*\d+)", re.IGNORECASE),
            re.compile(r"(\bAND\b\s+\d+\s*=\s*\d+)", re.IGNORECASE),
            re.compile(r"('|\")\s*(OR|AND)\s*('|\")", re.IGNORECASE),
            re.compile(r"(--|#|/\*)", re.IGNORECASE),
        ]
        self.xss_patterns = [
            re.compile(r"<script[^>]*>", re.IGNORECASE),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"onerror\s*=", re.IGNORECASE),
            re.compile(r"onload\s*=", re.IGNORECASE),
            re.compile(r"<iframe[^>]*>", re.IGNORECASE),
            re.compile(r"<img[^>]*onerror", re.IGNORECASE),
            re.compile(r"alert\s*\(", re.IGNORECASE),
        ]
        self.brute_force_pattern = re.compile(r'(failed|invalid|incorrect).*(password|login|authentication)', re.IGNORECASE)
        self.port_scan_pattern = re.compile(r'(port\s*scan|nmap|masscan|syn\s*scan)', re.IGNORECASE)

    def analyze(self, log_content, log_type='generic'):
        if not log_content:
            return self._empty_result()

        lines = log_content.split('\n')
        total_entries = len([l for l in lines if l.strip()])

        ip_addresses = self._extract_ips(log_content)
        user_agents = self._extract_user_agents(log_content)
        timestamps = self._extract_timestamps(log_content)

        failed_logins = 0
        successful_logins = 0
        brute_force_attempts = 0
        sql_injection_attempts = 0
        xss_attempts = 0
        port_scan_attempts = 0

        suspicious_entries = []
        anomalies = []

        for line in lines:
            if not line.strip():
                continue

            if self.brute_force_pattern.search(line):
                brute_force_attempts += 1
                suspicious_entries.append(line.strip())
                if 'failed' in line.lower() or 'invalid' in line.lower() or 'incorrect' in line.lower():
                    failed_logins += 1
                else:
                    successful_logins += 1

            if any(pattern.search(line) for pattern in self.sql_injection_patterns):
                sql_injection_attempts += 1
                suspicious_entries.append(line.strip())

            if any(pattern.search(line) for pattern in self.xss_patterns):
                xss_attempts += 1
                suspicious_entries.append(line.strip())

            if self.port_scan_pattern.search(line):
                port_scan_attempts += 1
                suspicious_entries.append(line.strip())

        if 'login' in log_type.lower() or 'auth' in log_type.lower():
            for line in lines:
                if 'success' in line.lower() and ('login' in line.lower() or 'auth' in line.lower()):
                    successful_logins += 1

        if brute_force_attempts > 5:
            anomalies.append(f'Possible brute force attack detected: {brute_force_attempts} attempts')
        if sql_injection_attempts > 0:
            anomalies.append(f'SQL injection attempts detected: {sql_injection_attempts}')
        if xss_attempts > 0:
            anomalies.append(f'XSS attempts detected: {xss_attempts}')
        if port_scan_attempts > 0:
            anomalies.append(f'Port scanning activity detected: {port_scan_attempts}')

        top_ips = Counter(ip_addresses).most_common(10)
        patterns = self._detect_patterns(lines)

        severity = 'low'
        total_suspicious = brute_force_attempts + sql_injection_attempts + xss_attempts + port_scan_attempts
        if total_suspicious > 20:
            severity = 'critical'
        elif total_suspicious > 10:
            severity = 'high'
        elif total_suspicious > 3:
            severity = 'medium'

        return {
            'total_entries': total_entries,
            'suspicious_entries': len(suspicious_entries),
            'failed_logins': failed_logins,
            'successful_logins': successful_logins,
            'brute_force_attempts': brute_force_attempts,
            'sql_injection_attempts': sql_injection_attempts,
            'xss_attempts': xss_attempts,
            'port_scan_attempts': port_scan_attempts,
            'ip_addresses': '\n'.join([f"{ip}: {count}" for ip, count in top_ips]),
            'user_agents': '\n'.join(user_agents[:10]),
            'anomalies_found': '\n'.join(anomalies) if anomalies else 'No anomalies detected',
            'patterns_detected': '\n'.join(patterns) if patterns else 'No significant patterns detected',
            'severity': severity,
            'suspicious_logs': suspicious_entries[:50]
        }

    def _extract_ips(self, text):
        return self.ip_pattern.findall(text)

    def _extract_user_agents(self, text):
        return self.user_agent_pattern.findall(text)

    def _extract_timestamps(self, text):
        return self.timestamp_pattern.findall(text)

    def _detect_patterns(self, lines):
        patterns = []
        if len(lines) > 100:
            patterns.append('High volume of log entries detected')

        repeated_ips = Counter(self._extract_ips('\n'.join(lines)))
        for ip, count in repeated_ips.most_common(3):
            if count > 10:
                patterns.append(f'High activity from IP {ip}: {count} entries')

        return patterns

    def _empty_result(self):
        return {
            'total_entries': 0,
            'suspicious_entries': 0,
            'failed_logins': 0,
            'successful_logins': 0,
            'brute_force_attempts': 0,
            'sql_injection_attempts': 0,
            'xss_attempts': 0,
            'port_scan_attempts': 0,
            'ip_addresses': '',
            'user_agents': '',
            'anomalies_found': 'No log content provided',
            'patterns_detected': '',
            'severity': 'low',
            'suspicious_logs': []
        }