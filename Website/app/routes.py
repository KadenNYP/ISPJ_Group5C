from flask import render_template, request, redirect, url_for, flash, Blueprint

main = Blueprint('routes', __name__)


@main.route('/')
def index():
    return render_template('index.html')

