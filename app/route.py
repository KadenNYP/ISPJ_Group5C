from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import *

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
def Essential_Plan():
    return render_template("Login-home/Essential_Plan.html")


@route.route('/enhanced_plan')
def Enhanced_Plan():
    return render_template("Login-home/Enhanced_Plan.html")


@route.route('/elite_plan')
def Elite_Plan():
    return render_template("Login-home/Elite_Plan.html")


@route.route('/plus_plan')
def Plus_Plan():
    return render_template("Login-home/Plus_Plan.html")
