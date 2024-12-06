from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from .init import db
import re

auth = Blueprint('auth', __name__)

# variables
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_TIME = timedelta(seconds=30)


def is_valid_email(email):
    email_address = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return re.match(email_address, email) is not None


@auth.route('signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif is_valid_email(email) == False:
            flash('Invalid email address.', category='error')
        else:
            user = User(first_name=first_name, last_name=last_name, email=email,
                        password=generate_password_hash(password1, method='sha256'))
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('user/signup.html')


@auth.route('login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the user is locked out
            if user.lockout_time and datetime() < user.lockout_time:
                flash('Your account is locked out.', category='error')
                return redirect(url_for('auth.login'))

            if check_password_hash(user.password, password):
                # Reset failed login attempts and lockout time on successful login
                user.failed_login_attempts = 0
                user.lockout_time = None
                db.session.commit()
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user.lockout_time = datetime() + LOCKOUT_TIME
                    flash('Too many failed login attempts. Your account is locked out.', category='error')
                else:
                    flash('Incorrect password, try again.', category='error')
                db.session.commit()
        else:
            flash('Email is incorrect.', category='error')

    return render_template('user/login.html', user=current_user)


@auth.route('logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home.index'))