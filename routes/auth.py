from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
from services.audit_service import log_action
from utils.helpers import generate_otp, validate_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter((User.username == username) | (User.email == username)).first()

        if not user:
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html')

        if user.is_locked():
            flash('Account is locked. Please try again later.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Account is deactivated. Contact administrator.', 'danger')
            return render_template('auth/login.html')

        if user.check_password(password):
            user.reset_login_attempts()
            user.last_login = datetime.utcnow()
            user.last_login_ip = request.remote_addr
            db.session.commit()

            login_user(user, remember=remember)
            session.permanent = True

            log_action(user.id, 'login', 'auth', None, 'User logged in')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            user.record_failed_login()
            log_action(user.id, 'login_failed', 'auth', None, 'Failed login attempt', status='failed')
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', '').strip()
        badge_number = request.form.get('badge_number', '').strip()
        phone = request.form.get('phone', '').strip()

        if not all([username, email, password, confirm_password, full_name]):
            flash('All required fields must be filled', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return render_template('auth/register.html')

        if not validate_email(email):
            flash('Invalid email address', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            department=department,
            badge_number=badge_number,
            phone=phone,
            role='analyst'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        log_action(user.id, 'register', 'auth', user.id, 'New user registered')
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_action(current_user.id, 'logout', 'auth', None, 'User logged out')
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            otp = generate_otp()
            user.otp_secret = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
            db.session.commit()
            session['reset_email'] = email
            session['reset_otp'] = otp
            flash('OTP has been generated. Check your email (demo: OTP shown in session).', 'info')
            return redirect(url_for('auth.verify_otp'))
        flash('Email not found', 'danger')
    return render_template('auth/forgot_password.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        email = session.get('reset_email')
        expected_otp = session.get('reset_otp')

        if not email or not expected_otp:
            flash('Session expired. Please try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        user = User.query.filter_by(email=email).first()
        if not user or user.otp_expiry < datetime.utcnow():
            flash('OTP expired. Please request a new one.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        if otp == expected_otp:
            session['reset_verified'] = True
            flash('OTP verified. Set your new password.', 'success')
            return redirect(url_for('auth.reset_password'))
        flash('Invalid OTP', 'danger')
    return render_template('auth/verify_otp.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('reset_verified'):
        flash('Please verify OTP first', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/reset_password.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return render_template('auth/reset_password.html')

        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            user.otp_secret = None
            user.otp_expiry = None
            db.session.commit()
            session.clear()
            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        flash('User not found', 'danger')
    return render_template('auth/reset_password.html')