-- AI-Powered Cyber Crime Investigation & Threat Intelligence Platform
-- Complete MySQL Database Schema Script
-- Compatible with XAMPP/phpMyAdmin
-- Database: cyber_investigation_db

CREATE DATABASE IF NOT EXISTS cyber_investigation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cyber_investigation_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst',
    department VARCHAR(100),
    badge_number VARCHAR(50) UNIQUE,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    otp_secret VARCHAR(32),
    otp_expiry DATETIME,
    failed_login_attempts INT DEFAULT 0,
    locked_until DATETIME,
    last_login DATETIME,
    last_login_ip VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- 2. Cases Table
CREATE TABLE IF NOT EXISTS cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    classification VARCHAR(50),
    case_type VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'low',
    created_by INT NOT NULL,
    assigned_to INT,
    assigned_date DATETIME,
    opened_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_date DATETIME,
    due_date DATETIME,
    location VARCHAR(200),
    jurisdiction VARCHAR(100),
    victim_name VARCHAR(120),
    victim_contact VARCHAR(120),
    suspect_name VARCHAR(120),
    suspect_contact VARCHAR(120),
    financial_loss DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    summary TEXT,
    tags VARCHAR(500),
    is_confidential BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    INDEX idx_case_number (case_number),
    INDEX idx_status (status),
    INDEX idx_priority (priority)
) ENGINE=InnoDB;

-- 3. Evidence Table
CREATE TABLE IF NOT EXISTS evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    evidence_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    evidence_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size BIGINT,
    file_hash_md5 VARCHAR(32),
    file_hash_sha1 VARCHAR(40),
    file_hash_sha256 VARCHAR(64),
    mime_type VARCHAR(100),
    source VARCHAR(200),
    collected_by INT,
    collected_date DATETIME,
    collection_method VARCHAR(200),
    chain_of_custody TEXT,
    status VARCHAR(30) DEFAULT 'collected',
    integrity_status VARCHAR(30) DEFAULT 'verified',
    is_encrypted BOOLEAN DEFAULT FALSE,
    encryption_method VARCHAR(100),
    storage_location VARCHAR(200),
    retention_date DATETIME,
    disposition VARCHAR(50),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (collected_by) REFERENCES users(id),
    INDEX idx_evidence_number (evidence_number),
    INDEX idx_case_id (case_id)
) ENGINE=InnoDB;

-- 4. IOCs Table
CREATE TABLE IF NOT EXISTS iocs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    ioc_type VARCHAR(30) NOT NULL,
    ioc_value VARCHAR(500) NOT NULL,
    description TEXT,
    threat_level VARCHAR(20) DEFAULT 'medium',
    confidence INT DEFAULT 50,
    source VARCHAR(200),
    first_seen DATETIME,
    last_seen DATETIME,
    status VARCHAR(30) DEFAULT 'active',
    tags VARCHAR(500),
    related_malware VARCHAR(200),
    related_campaign VARCHAR(200),
    tlp_level VARCHAR(10) DEFAULT 'amber',
    is_shared BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_ioc_value (ioc_value),
    INDEX idx_ioc_type (ioc_type)
) ENGINE=InnoDB;

-- 5. Threat Intel Table
CREATE TABLE IF NOT EXISTS threat_intel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    threat_type VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'medium',
    confidence INT DEFAULT 50,
    source VARCHAR(200),
    source_url VARCHAR(500),
    published_date DATETIME,
    first_seen DATETIME,
    last_seen DATETIME,
    affected_platforms VARCHAR(500),
    attack_vector VARCHAR(200),
    impact TEXT,
    mitigation TEXT,
    indicators TEXT,
    related_campaigns VARCHAR(500),
    tlp_level VARCHAR(10) DEFAULT 'amber',
    status VARCHAR(30) DEFAULT 'active',
    tags VARCHAR(500),
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 6. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    status VARCHAR(20) DEFAULT 'success',
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- 7. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    notification_type VARCHAR(50) DEFAULT 'info',
    severity VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME,
    link VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB;

-- 8. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    report_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(10) DEFAULT 'pdf',
    content TEXT,
    file_path VARCHAR(500),
    generated_by INT NOT NULL,
    status VARCHAR(30) DEFAULT 'draft',
    classification VARCHAR(20) DEFAULT 'confidential',
    is_final BOOLEAN DEFAULT FALSE,
    approved_by INT,
    approved_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 9. Link Analysis Table
CREATE TABLE IF NOT EXISTS link_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    analysis_name VARCHAR(200) NOT NULL,
    description TEXT,
    graph_data LONGTEXT,
    nodes_count INT DEFAULT 0,
    edges_count INT DEFAULT 0,
    central_nodes TEXT,
    communities TEXT,
    analysis_type VARCHAR(50) DEFAULT 'network',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 10. Malware Analysis Table
CREATE TABLE IF NOT EXISTS malware_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_hash_md5 VARCHAR(32),
    file_hash_sha1 VARCHAR(40),
    file_hash_sha256 VARCHAR(64),
    file_size BIGINT,
    file_type VARCHAR(50),
    malware_family VARCHAR(100),
    malware_type VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'medium',
    confidence INT DEFAULT 50,
    detection_ratio VARCHAR(20),
    behavior_analysis TEXT,
    static_analysis TEXT,
    dynamic_analysis TEXT,
    strings_found LONGTEXT,
    urls_found TEXT,
    ips_found TEXT,
    registry_changes TEXT,
    file_changes TEXT,
    network_connections TEXT,
    persistence_mechanisms TEXT,
    yara_rules TEXT,
    mitre_techniques VARCHAR(500),
    sandbox_report TEXT,
    status VARCHAR(30) DEFAULT 'analyzed',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 11. Log Analysis Table
CREATE TABLE IF NOT EXISTS log_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    log_source VARCHAR(200),
    file_name VARCHAR(255),
    total_entries INT DEFAULT 0,
    suspicious_entries INT DEFAULT 0,
    analysis_results LONGTEXT,
    anomalies_found TEXT,
    patterns_detected TEXT,
    ip_addresses TEXT,
    user_agents TEXT,
    failed_logins INT DEFAULT 0,
    successful_logins INT DEFAULT 0,
    brute_force_attempts INT DEFAULT 0,
    sql_injection_attempts INT DEFAULT 0,
    xss_attempts INT DEFAULT 0,
    port_scan_attempts INT DEFAULT 0,
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(30) DEFAULT 'analyzed',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 12. Email Header Analysis Table
CREATE TABLE IF NOT EXISTS email_header_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    subject VARCHAR(500),
    sender_email VARCHAR(255),
    sender_name VARCHAR(255),
    recipient_email VARCHAR(255),
    reply_to VARCHAR(255),
    date_sent DATETIME,
    message_id VARCHAR(255),
    received_chain LONGTEXT,
    authentication_results TEXT,
    spf_result VARCHAR(50),
    dkim_result VARCHAR(50),
    dmarc_result VARCHAR(50),
    x_headers TEXT,
    return_path VARCHAR(255),
    envelope_from VARCHAR(255),
    source_ip VARCHAR(45),
    source_hostname VARCHAR(255),
    user_agent VARCHAR(500),
    is_suspicious BOOLEAN DEFAULT FALSE,
    spoofing_detected BOOLEAN DEFAULT FALSE,
    phishing_indicators TEXT,
    analysis_notes TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 13. OCR Documents Table
CREATE TABLE IF NOT EXISTS ocr_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    extracted_text LONGTEXT,
    confidence_score FLOAT DEFAULT 0.0,
    language VARCHAR(20) DEFAULT 'eng',
    page_count INT DEFAULT 1,
    entities_found TEXT,
    ocr_engine VARCHAR(50) DEFAULT 'tesseract',
    status VARCHAR(30) DEFAULT 'processed',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 14. PDF Intelligence Table
CREATE TABLE IF NOT EXISTS pdf_intelligence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    page_count INT DEFAULT 0,
    metadata TEXT,
    extracted_text LONGTEXT,
    summary TEXT,
    entities_found TEXT,
    urls_found TEXT,
    emails_found TEXT,
    phone_numbers TEXT,
    dates_found TEXT,
    is_malicious BOOLEAN DEFAULT FALSE,
    javascript_detected BOOLEAN DEFAULT FALSE,
    embedded_files TEXT,
    suspicious_indicators TEXT,
    status VARCHAR(30) DEFAULT 'processed',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 15. Timeline Events Table
CREATE TABLE IF NOT EXISTS timeline_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    event_title VARCHAR(200) NOT NULL,
    event_description TEXT,
    event_date DATETIME NOT NULL,
    event_type VARCHAR(50),
    event_source VARCHAR(200),
    related_evidence_id INT,
    related_ioc_id INT,
    importance VARCHAR(20) DEFAULT 'normal',
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (related_evidence_id) REFERENCES evidence(id),
    FOREIGN KEY (related_ioc_id) REFERENCES iocs(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_case_id (case_id),
    INDEX idx_event_date (event_date)
) ENGINE=InnoDB;

-- 16. System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string',
    description VARCHAR(500),
    is_encrypted BOOLEAN DEFAULT FALSE,
    updated_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 17. Backup Records Table
CREATE TABLE IF NOT EXISTS backup_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_name VARCHAR(200) NOT NULL,
    backup_type VARCHAR(20) DEFAULT 'full',
    file_path VARCHAR(500),
    file_size BIGINT,
    status VARCHAR(30) DEFAULT 'completed',
    description TEXT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 18. Search Index Table
CREATE TABLE IF NOT EXISTS search_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    title VARCHAR(500),
    content LONGTEXT,
    tags VARCHAR(500),
    search_vector LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_entity_type (entity_type),
    INDEX idx_entity_id (entity_id),
    FULLTEXT INDEX ft_search (title, content, tags)
) ENGINE=InnoDB;

-- 19. Extracted Entities Table
CREATE TABLE IF NOT EXISTS extracted_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    entity_type VARCHAR(30) NOT NULL,
    entity_value VARCHAR(500) NOT NULL,
    context TEXT,
    confidence FLOAT DEFAULT 0.0,
    source_document VARCHAR(255),
    source_type VARCHAR(50),
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_entity_type (entity_type),
    INDEX idx_case_id (case_id)
) ENGINE=InnoDB;

-- 20. Document Summaries Table
CREATE TABLE IF NOT EXISTS document_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    document_type VARCHAR(50),
    document_name VARCHAR(255),
    original_text LONGTEXT,
    summary_text LONGTEXT,
    summary_length INT,
    compression_ratio FLOAT,
    key_points TEXT,
    sentiment VARCHAR(20),
    language VARCHAR(20) DEFAULT 'en',
    model_used VARCHAR(100),
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- Insert default admin user (password: admin123)
-- Password hash generated using Werkzeug's generate_password_hash
INSERT INTO users (username, email, password_hash, full_name, role, department, is_active, is_verified)
VALUES ('admin', 'admin@cyberintel.local', 'pbkdf2:sha256:600000$placeholder$placeholder', 'System Administrator', 'admin', 'IT Security', TRUE, TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('platform_name', 'AI-Powered Cyber Crime Investigation Platform', 'string', 'Platform display name'),
('max_upload_size', '52428800', 'integer', 'Maximum file upload size in bytes'),
('session_timeout', '28800', 'integer', 'Session timeout in seconds'),
('password_min_length', '8', 'integer', 'Minimum password length'),
('login_attempts_limit', '5', 'integer', 'Maximum failed login attempts before lockout'),
('ai_summary_max_length', '500', 'integer', 'Maximum AI summary length'),
('default_page_size', '20', 'integer', 'Default pagination size')
ON DUPLICATE KEY UPDATE setting_key=setting_key;