from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
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


@auth.route('signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role_name = request.form.get('role')
        
        # Debugging
        print(f"Signup form data: first_name={first_name}, last_name={last_name}, email={email}, password={password}, confirm_password={confirm_password}")

        user = User.query.filter_by(email=email).first()

        # Check if the email already exists
        if user:
            flash('Email already exists.', category='error')
        elif is_valid_email(email) == False:
            flash('Invalid email address.', category='error')
        elif password != confirm_password:
            flash('Passwords do not match.', category='error')
        else:
            role = Role.query.filter_by(name=role_name).first()
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, role=role)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('route.index'))

    return render_template('user/signup.html')


@auth.route('login', methods=["GET", "POST"])
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
                return redirect(url_for('route.index'))
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
    return redirect(url_for('route.index'))

@auth.route('profile', methods=["GET", "POST"])
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@auth.route('userdb', methods=["GET", "POST"])
@login_required
def userdb():
    role_filter = request.args.get('role', '')
    
    if role_filter == 'customer' or role_filter == 'staff':
        user_list = User.query.filter(User.role_id == 1).all()

    elif role_filter == 'staff':
        user_list = User.query.filter(User.role_id != 1).all()

    else:
        user_list = User.query.all()

    count = len(user_list)
    print(role_filter)
    for row in user_list:
        print(row.role_id)
            

    return render_template('user/userdb.html', role_filter=role_filter, user_list=user_list, count=count)