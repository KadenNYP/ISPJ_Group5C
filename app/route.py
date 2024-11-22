from flask import Blueprint, render_template, redirect, url_for, flash

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
