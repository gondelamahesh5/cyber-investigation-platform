"""
Database initialization script for the Cyber Crime Investigation Platform.
Creates the database, tables, and a default admin user.
"""
import os
import sys
from getpass import getpass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app
from extensions import db
from models.user import User
from models.settings import SystemSetting
from werkzeug.security import generate_password_hash


def init_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully.")

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("\nCreating default admin user...")
            admin = User(
                username='admin',
                email='admin@cyberintel.local',
                full_name='System Administrator',
                role='admin',
                department='IT Security',
                is_active=True,
                is_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists.")

        default_settings = [
            ('platform_name', 'AI-Powered Cyber Crime Investigation Platform', 'string', 'Platform display name'),
            ('max_upload_size', '52428800', 'integer', 'Maximum file upload size in bytes'),
            ('session_timeout', '28800', 'integer', 'Session timeout in seconds'),
            ('password_min_length', '8', 'integer', 'Minimum password length'),
            ('login_attempts_limit', '5', 'integer', 'Maximum failed login attempts before lockout'),
            ('ai_summary_max_length', '500', 'integer', 'Maximum AI summary length'),
            ('default_page_size', '20', 'integer', 'Default pagination size'),
        ]

        for key, value, stype, desc in default_settings:
            setting = SystemSetting.query.filter_by(setting_key=key).first()
            if not setting:
                setting = SystemSetting(
                    setting_key=key,
                    setting_value=value,
                    setting_type=stype,
                    description=desc
                )
                db.session.add(setting)

        db.session.commit()
        print("Default settings created.")
        print("\nDatabase initialization complete!")
        print("\nYou can now start the application with: python app.py")
        print("Access the platform at: http://localhost:5000")


if __name__ == '__main__':
    init_database()