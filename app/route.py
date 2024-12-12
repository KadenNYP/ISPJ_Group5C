from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from .models import *
from .auth import current_user

route = Blueprint('route', __name__)

"""@route.before_app_request
def before_request():
    if 'user' in session:
        g.user = session['user']
    else:
        g.user = None"""


@route.route('/')
def index():
    return render_template("home/index.html")


@route.route('/plans')
def Plans_Overview():
    return render_template("home/Plans.html")


@route.route('/policy')
def PolicyTerms():
    return render_template("home/Policy&Terms.html")


@route.route('/contact', methods=["GET", "POST"])
def ContactSupport():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not name or not email or not subject or not message:
            flash("All fields are required!", "danger")
            return redirect(url_for('contact'))

        try:
            new_message = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(new_message)
            db.session.commit()
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again later.", "danger")
            print(f"Error: {e}")

        return redirect(url_for('route.ContactSupport'))

    return render_template('home/Contact.html')


@route.route('/essential_plan')
@login_required
def Essential_Plan():
    if current_user:
        return render_template("Login-home/Essential_Plan.html")


@route.route('/enhanced_plan')
@login_required
def Enhanced_Plan():
    if current_user:
        return render_template("Login-home/Enhanced_Plan.html")


@route.route('/elite_plan')
@login_required
def Elite_Plan():
    if current_user:
        return render_template("Login-home/Elite_Plan.html")


@route.route('/plus_plan')
@login_required
def Plus_Plan():
    if current_user:
        return render_template("Login-home/Plus_Plan.html")


@route.route('/purchase/1')
@login_required
def purchase_personal_info():
    return render_template("Login-home/Purchase_Personal Info.html")
