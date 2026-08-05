import os
import subprocess
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.settings import SystemSetting
from models.backup import BackupRecord
from models.audit import AuditLog
from services.audit_service import log_action
from utils.decorators import admin_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def index():
    settings = SystemSetting.query.all()
    return render_template('settings/index.html', settings=settings)


@settings_bp.route('/settings/general', methods=['POST'])
@login_required
def update_general():
    setting_key = request.form.get('setting_key', '')
    setting_value = request.form.get('setting_value', '')

    if not setting_key:
        flash('Setting key is required', 'danger')
        return redirect(url_for('settings.index'))

    setting = SystemSetting.query.filter_by(setting_key=setting_key).first()
    if setting:
        setting.setting_value = setting_value
        setting.updated_by = current_user.id
    else:
        setting = SystemSetting(
            setting_key=setting_key,
            setting_value=setting_value,
            setting_type='string',
            updated_by=current_user.id
        )
        db.session.add(setting)

    db.session.commit()
    log_action(current_user.id, 'update_setting', 'settings', setting.id, f'Updated setting {setting_key}')
    flash('Settings updated successfully', 'success')
    return redirect(url_for('settings.index'))


@settings_bp.route('/settings/users')
@admin_required
def users():
    users = User.query.all()
    return render_template('settings/users.html', users=users)


@settings_bp.route('/settings/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'danger')
        return redirect(url_for('settings.users'))

    user.is_active = not user.is_active
    db.session.commit()
    log_action(current_user.id, 'toggle_user', 'user', user.id, f'Toggled user {user.username} active={user.is_active}')
    flash(f'User {user.username} {"activated" if user.is_active else "deactivated"}', 'success')
    return redirect(url_for('settings.users'))


@settings_bp.route('/settings/users/<int:user_id>/role', methods=['POST'])
@admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', '')
    valid_roles = ['admin', 'analyst', 'investigator', 'viewer']

    if new_role not in valid_roles:
        flash('Invalid role', 'danger')
        return redirect(url_for('settings.users'))

    user.role = new_role
    db.session.commit()
    log_action(current_user.id, 'change_role', 'user', user.id, f'Changed role of {user.username} to {new_role}')
    flash(f'Role changed to {new_role}', 'success')
    return redirect(url_for('settings.users'))


@settings_bp.route('/settings/audit-logs')
@login_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    action = request.args.get('action', '')
    user_id = request.args.get('user_id', type=int)

    query = AuditLog.query
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=25, error_out=False)
    users = User.query.all()
    return render_template('settings/audit_logs.html', logs=logs, users=users, action=action, user_id=user_id)


@settings_bp.route('/settings/backup', methods=['GET', 'POST'])
@admin_required
def backup():
    if request.method == 'POST':
        backup_type = request.form.get('backup_type', 'full')
        description = request.form.get('description', '')

        backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup = BackupRecord(
            backup_name=backup_name,
            backup_type=backup_type,
            description=description,
            created_by=current_user.id,
            status='in_progress'
        )
        db.session.add(backup)
        db.session.commit()

        try:
            backup_path = os.path.join(db.engine.url.database if hasattr(db.engine.url, 'database') else 'backups', backup_name)
            
            import json
            data = {}
            for table_name in db.metadata.tables.keys():
                result = db.session.execute(db.text(f'SELECT * FROM {table_name}'))
                rows = [dict(row._mapping) for row in result]
                data[table_name] = rows

            from flask import current_app
            backup_folder = current_app.config['BACKUP_FOLDER']
            backup_file = os.path.join(backup_folder, f"{backup_name}.json")

            for row_list in data.values():
                for row in row_list:
                    for key, value in list(row.items()):
                        if hasattr(value, 'isoformat'):
                            row[key] = value.isoformat()

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, default=str, indent=2)

            backup.file_path = backup_file
            backup.file_size = os.path.getsize(backup_file)
            backup.status = 'completed'
            backup.completed_at = datetime.utcnow()
            db.session.commit()

            log_action(current_user.id, 'create_backup', 'backup', backup.id, f'Created backup {backup_name}')
            flash('Backup created successfully', 'success')
        except Exception as e:
            backup.status = 'failed'
            db.session.commit()
            flash(f'Backup failed: {str(e)}', 'danger')

        return redirect(url_for('settings.backup'))

    backups = BackupRecord.query.order_by(BackupRecord.created_at.desc()).all()
    return render_template('settings/backup.html', backups=backups)


@settings_bp.route('/settings/backup/<int:backup_id>/restore', methods=['POST'])
@admin_required
def restore_backup(backup_id):
    backup = BackupRecord.query.get_or_404(backup_id)
    if not backup.file_path or not os.path.exists(backup.file_path):
        flash('Backup file not found', 'danger')
        return redirect(url_for('settings.backup'))

    try:
        import json
        with open(backup.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for table_name, rows in data.items():
            if rows:
                db.session.execute(db.text(f'DELETE FROM {table_name}'))
                if rows:
                    columns = list(rows[0].keys())
                    placeholders = ', '.join([':' + col for col in columns])
                    for row in rows:
                        db.session.execute(
                            db.text(f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'),
                            row
                        )

        db.session.commit()
        log_action(current_user.id, 'restore_backup', 'backup', backup.id, f'Restored backup {backup.backup_name}')
        flash('Backup restored successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Restore failed: {str(e)}', 'danger')

    return redirect(url_for('settings.backup'))


@settings_bp.route('/settings/backup/<int:backup_id>/download')
@admin_required
def download_backup(backup_id):
    backup = BackupRecord.query.get_or_404(backup_id)
    if backup.file_path and os.path.exists(backup.file_path):
        return send_file(backup.file_path, as_attachment=True, download_name=os.path.basename(backup.file_path))
    flash('Backup file not found', 'danger')
    return redirect(url_for('settings.backup'))


@settings_bp.route('/settings/backup/<int:backup_id>/delete', methods=['POST'])
@admin_required
def delete_backup(backup_id):
    backup = BackupRecord.query.get_or_404(backup_id)
    backup_name = backup.backup_name
    file_path = backup.file_path

    db.session.delete(backup)
    db.session.commit()

    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    log_action(current_user.id, 'delete_backup', 'backup', backup_id, f'Deleted backup {backup_name}')
    flash('Backup deleted', 'success')
    return redirect(url_for('settings.backup'))


@settings_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')

        user = db.session.get(User, current_user.id)
        user.full_name = full_name
        user.phone = phone
        user.department = department

        if current_password and new_password:
            if not user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('settings.profile'))
            if len(new_password) < 8:
                flash('New password must be at least 8 characters', 'danger')
                return redirect(url_for('settings.profile'))
            user.set_password(new_password)

        db.session.commit()
        log_action(current_user.id, 'update_profile', 'user', user.id, 'Updated profile')
        flash('Profile updated successfully', 'success')
        return redirect(url_for('settings.profile'))

    return render_template('settings/profile.html')


@settings_bp.route('/settings/notifications')
@login_required
def notifications():
    from services.notification_service import get_user_notifications
    notifications = get_user_notifications(current_user.id)
    return render_template('settings/notifications.html', notifications=notifications)


@settings_bp.route('/settings/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    from services.notification_service import mark_as_read
    mark_as_read(notification_id, current_user.id)
    return redirect(url_for('settings.notifications'))


@settings_bp.route('/settings/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    from services.notification_service import mark_all_as_read
    count = mark_all_as_read(current_user.id)
    flash(f'Marked {count} notifications as read', 'success')
    return redirect(url_for('settings.notifications'))