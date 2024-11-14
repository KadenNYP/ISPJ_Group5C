from flask import Blueprint, render_template, redirect, url_for, flash

auth = Blueprint('auth', __name__)


@auth.route('signup', methods=['POST'])
def signup():
    # do something
    flash('Account created. Thank you for signing up.\nWelcome to Healthcare Insurance!')
    return redirect(url_for('index'))


@auth.route('login', methods=['POST'])
def login():
    # do something
    flash('Welcome to Healthcare Insurance!')
    return redirect(url_for('index'))


@auth.route('logout')
def logout():
    # do something
    flash('You have been logged out.')
    return redirect(url_for('index'))
