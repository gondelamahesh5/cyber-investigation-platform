# AI-Powered Cyber Crime Investigation & Threat Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3%2B-purple)

A production-ready, enterprise-grade cyber crime investigation platform powered by AI for threat intelligence, evidence management, and automated analysis.

## 🚀 Features

### Core Functionality
- **Case Management** - Full lifecycle case tracking with priorities, statuses, and assignments
- **Evidence Management** - Secure file uploads with hash verification (MD5, SHA1, SHA256)
- **IOC Management** - Track Indicators of Compromise with threat levels and TLP classification
- **Threat Intelligence** - Monitor threats with severity, confidence scores, and mitigation strategies
- **AI-Powered Analysis** - 8 specialized AI tools for automated investigation

### AI Analysis Tools
- **Document Summarization** - Extractive summarization with sentiment analysis
- **Named Entity Extraction** - Identify IPs, URLs, emails, hashes, CVEs, and more
- **Link Analysis** - NetworkX-powered graph analysis for relationship mapping
- **Log Analysis** - Detect brute force attacks, SQL injection, XSS, port scanning
- **Email Header Analysis** - SPF/DKIM/DMARC validation and spoofing detection
- **OCR Processing** - Extract text from images using Tesseract
- **PDF Intelligence** - Malicious content detection and entity extraction
- **Malware Analysis** - String extraction, hash calculation, family detection

### Security Features
- Role-Based Access Control (RBAC) with 4 roles
- CSRF protection on all forms
- Rate limiting to prevent abuse
- Secure file upload validation
- SQL injection and XSS prevention
- Audit logging for all actions
- Password strength enforcement
- Account lockout after failed attempts
- Encrypted sensitive data

### Additional Features
- Interactive dashboard with real-time charts
- Investigation timeline visualization
- Report generation (PDF, CSV, Excel)
- Global search across all entities
- Notifications system
- Backup and restore functionality
- Responsive design for all devices

## 📋 Requirements

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.0
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.1
Werkzeug==3.0.1
SQLAlchemy==2.0.23
python-dotenv==1.0.0
gunicorn==21.2.0
Pillow==10.1.0
pytesseract==0.3.10
pdfplumber==0.10.3
networkx==3.2.1
textblob==0.17.1
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
python-magic==0.4.27
validators==0.22.0
cryptography==41.0.7
```

## 🔧 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/cyber-investigation-platform.git
cd cyber-investigation-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///cyber_investigation.db
FLASK_ENV=production
```

### 5. Initialize Database
```bash
python init_db.py
```

Default credentials:
- Username: `admin`
- Password: `admin123`

### 6. Run Application
```bash
# Development
python app.py

# Production
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Access the application at: `http://localhost:5000`

## 🏗️ Project Structure

```
├── app.py                      # Main Flask application
├── init_db.py                  # Database initialization
├── requirements.txt             # Python dependencies
├── config/
│   └── config.py               # Configuration classes
├── models/
│   ├── user.py                 # User model
│   ├── case.py                 # Case model
│   ├── evidence.py             # Evidence model
│   ├── ioc.py                  # IOC model
│   ├── threat.py               # Threat intelligence model
│   ├── audit.py                # Audit logging model
│   ├── notification.py         # Notification model
│   ├── report.py               # Report model
│   └── [other models...]
├── routes/
│   ├── auth.py                 # Authentication routes
│   ├── dashboard.py            # Dashboard routes
│   ├── cases.py                # Case management
│   ├── evidence.py             # Evidence management
│   ├── iocs.py                 # IOC management
│   ├── threats.py              # Threat intelligence
│   ├── analysis.py             # AI analysis tools
│   ├── reports.py              # Report generation
│   ├── settings.py             # User settings
│   └── api.py                  # REST API endpoints
├── services/
│   ├── audit_service.py        # Audit logging service
│   ├── notification_service.py # Notification service
│   └── file_service.py         # File handling service
├── ai/
│   ├── entity_extraction.py    # NER for IOCs
│   ├── summarizer.py           # Document summarization
│   ├── link_analysis.py        # Graph analysis
│   ├── log_analyzer.py         # Log pattern detection
│   ├── email_analyzer.py       # Email header analysis
│   ├── ocr_processor.py        # OCR processing
│   ├── pdf_analyzer.py         # PDF analysis
│   └── malware_analyzer.py     # Malware analysis
├── utils/
│   ├── helpers.py              # Utility functions
│   └── decorators.py           # Custom decorators
├── templates/
│   ├── base.html               # Base template
│   ├── auth/                   # Authentication pages
│   ├── dashboard/              # Dashboard pages
│   ├── cases/                  # Case management pages
│   ├── evidence/               # Evidence pages
│   ├── iocs/                   # IOC pages
│   ├── threats/                # Threat intel pages
│   ├── analysis/               # AI analysis pages
│   ├── reports/                # Report pages
│   └── settings/               # Settings pages
├── static/
│   ├── css/
│   │   ├── premium-theme.css   # Premium UI theme
│   │   └── style.css           # Custom styles
│   └── js/
│       └── main.js             # JavaScript functionality
├── database/
│   └── schema.sql              # MySQL schema
├── uploads/                    # Uploaded files
├── reports/                    # Generated reports
├── logs/                       # Application logs
├── backups/                    # Database backups
└── .gitignore                  # Git ignore file
```

## 🔐 Security

### Implemented Security Measures
- **CSRF Protection**: All forms protected with Flask-WTF CSRF tokens
- **Rate Limiting**: API endpoints and login forms rate-limited
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: Auto-escaping enabled in Jinja2 templates
- **Secure File Uploads**: Type validation, size limits, and hash verification
- **Password Security**: Werkzeug hashing with salt
- **Session Management**: Secure session configuration
- **RBAC**: Granular role-based access control
- **Audit Logging**: Comprehensive logging of all actions

### User Roles
1. **Admin** - Full system access
2. **Analyst** - Case and evidence management
3. **Investigator** - Investigation tools and analysis
4. **Viewer** - Read-only access

## 📊 Database Schema

### Core Tables
- **users** - User accounts with RBAC
- **cases** - Investigation cases
- **evidence** - Evidence items with hash verification
- **iocs** - Indicators of Compromise
- **threat_intel** - Threat intelligence data
- **audit_logs** - Comprehensive audit trail
- **notifications** - User notifications
- **reports** - Generated reports

### Relationships
- Users → Cases (created/assigned)
- Cases → Evidence (one-to-many)
- Cases → IOCs (many-to-many)
- Evidence → Audit Logs (one-to-many)
- All entities → Audit Logs (tracking)

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/register` - User registration
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset

### Cases
- `GET /cases` - List cases
- `POST /cases` - Create case
- `GET /cases/<id>` - View case
- `PUT /cases/<id>` - Update case
- `DELETE /cases/<id>` - Delete case

### Evidence
- `GET /evidence` - List evidence
- `POST /evidence/upload` - Upload evidence
- `GET /evidence/<id>` - View evidence
- `DELETE /evidence/<id>` - Delete evidence

### IOCs
- `GET /iocs` - List IOCs
- `POST /iocs` - Create IOC
- `GET /iocs/<id>` - View IOC
- `PUT /iocs/<id>` - Update IOC

### AI Analysis
- `POST /analysis/summarize` - Summarize document
- `POST /analysis/entities` - Extract entities
- `POST /analysis/links` - Analyze links
- `POST /analysis/logs` - Analyze logs
- `POST /analysis/email` - Analyze email
- `POST /analysis/ocr` - OCR processing
- `POST /analysis/pdf` - PDF analysis
- `POST /analysis/malware` - Malware analysis

### Reports
- `GET /reports` - List reports
- `POST /reports/generate` - Generate report
- `GET /reports/<id>` - Download report

## 🤖 AI Features

### Entity Extraction
Extracts the following entities from text:
- IP addresses (IPv4, IPv6)
- Email addresses
- URLs
- Domains
- File hashes (MD5, SHA1, SHA256)
- CVEs
- Bitcoin addresses
- Phone numbers
- Credit card numbers

### Log Analysis Patterns
- Brute force detection
- SQL injection attempts
- XSS attacks
- Port scanning
- Path traversal
- Command injection

### Email Analysis
- SPF record validation
- DKIM signature verification
- DMARC policy checking
- Spoofing detection
- Header analysis

## 📈 Performance Optimization

### Database
- Indexed columns for frequent queries
- Foreign key constraints
- Query optimization with eager loading
- Connection pooling

### Caching
- Static asset caching
- Template caching
- Query result caching (where applicable)

### Frontend
- Minified CSS and JS (production)
- Lazy loading for images
- Optimized asset loading
- Responsive image sizes

## 🚀 Deployment

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### With Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/cyber-investigation-platform/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### With Systemd Service
```ini
[Unit]
Description=Cyber Investigation Platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/cyber-investigation
ExecStart=/opt/cyber-investigation/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📝 Development

### Running Tests
```bash
pytest tests/ -v --cov=.
```

### Code Style
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For support and questions:
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com
- Issues: https://github.com/yourusername/cyber-investigation-platform/issues

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Chart.js for beautiful charts
- Bootstrap for responsive UI framework
- Font Awesome for icons

## 🔄 Changelog

### v1.0.0 (2026-01-01)
- Initial release
- Core investigation features
- AI analysis tools
- Enterprise UI
- Security hardening

---

**⚠️ Warning**: This software is for authorized cybersecurity investigations only. Ensure compliance with local laws and regulations before use.