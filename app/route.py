from flask import Blueprint, render_template, redirect, url_for, flash

route = Blueprint('route', __name__)

@route.route('/')
def index():
    return render_template("/home/index.html")
