from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from app.Security_Features_Function.Encryption import *
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

def mask_email(email):
    parts = email.split('@')
    masked_email = parts[0][0] + '***' + '@' + parts[1]
    return masked_email

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

        encryption_key = Fernet.generate_key().decode()

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
            user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, role=role, encryption_key=encryption_key)
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


@auth.route('delete_user', methods=["GET", "POST"])
@login_required
def delete_user():
    user_id = request.args.get('user_id')
    print(user_id)
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', category='success')
    return redirect(url_for('auth.userdb'))


@auth.route('profile', methods=["GET", "POST"])
@login_required
def profile():
    has_purchased_plan = db.session.query(Purchase_details).filter_by(email=current_user.email).first() is not None

    has_billing_info = db.session.query(BillingAddress).filter_by(email=current_user.email).first() is not None
    has_payment_info = db.session.query(Payment).filter_by(email=current_user.email).first() is not None
    has_complete_info = has_billing_info and has_payment_info
    has_claim_info = db.session.query(ClaimID).filter_by(email=current_user.email).first() is not None

    return render_template('user/profile.html', user=current_user, has_purchased_plan=has_purchased_plan, has_billing_info=has_complete_info, has_claim_info=has_claim_info)


@auth.route('userdb', methods=["GET", "POST"])
@login_required
def userdb():
    role_filter = request.args.get('role', '')
    
    if role_filter == 'customer':
        user_list = User.query.filter(User.role_id == 3).all()

    elif role_filter == 'staff':
        user_list = User.query.filter(User.role_id != 3).all()

    else:
        user_list = User.query.all()

    count = len(user_list)

    return render_template('user/userdb.html', role_filter=role_filter, user_list=user_list, count=count, mask_email=mask_email)


@auth.route('view_billing_address', methods=["GET", "POST"])
@login_required
def view_billing_address():
    user_id = request.args.get('user_id', 0)
    print(user_id)

    billingaddress_list = BillingAddress.query.filter(BillingAddress.user_id == user_id).all()
    
    if billingaddress_list is None:
        billingaddress_list = 0
    print(billingaddress_list)

    try:
        count = len(billingaddress_list)
    except:
        count = 0
    
    return render_template('user/view_billing_address.html', billingaddress_list=billingaddress_list, count=count, mask_email=mask_email)

@auth.route('view_claims', methods=["GET", "POST"])
@login_required
def view_claims():

    claim_list = ClaimID.query.all()
    
    if claim_list is None:
        claim_list = 0
    print(claim_list)

    try:
        count = len(claim_list)
    except:
        count = 0
    
    return render_template('user/view_claims.html', claim_list=claim_list, count=count, mask_email=mask_email)

@auth.route('view_claims_info', methods=["GET", "POST"])
@login_required
def view_claims_info():
    claim_id = request.args.get('claim_id', 0)
    general_id = request.args.get('general_id', 0)
    specific_id = request.args.get('specific_id', 0)

    print(f'claim_id is {claim_id}')
    print(f'general_id is {general_id}')
    print(f'specific_id is {specific_id}')

    claim_info = ClaimID.query.filter(ClaimID.id == claim_id).first()
    general_info = Claim_general_info.query.filter(ClaimID.id == general_id).first()
    specific_info = Claim_specific_info.query.filter(ClaimID.id == specific_id).first()
    
    print(claim_info)
    print(f'claim status is "{claim_info.status}"')
    print(general_info)
    print(specific_info)

    return render_template('user/view_claims_info.html', claim_info=claim_info, general_info=general_info, specific_info=specific_info, mask_email=mask_email)

@auth.route('update_claim_status', methods=["GET", "POST"])
@login_required
def update_claim_status():
    claim_id = request.args.get('claim_id', 0)
    status = request.args.get('status', 'In Progress')

    claim_info = ClaimID.query.filter(ClaimID.id == claim_id).first()
    claim_info.status = status

    db.session.commit()

    return redirect(url_for('auth.view_claims_info', claim_id=claim_id, general_id=claim_info.general_id, specific_id=claim_info.specific_id))