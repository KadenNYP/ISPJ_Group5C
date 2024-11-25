from flask import Blueprint, render_template, redirect, url_for, flash

auth = Blueprint('auth', __name__)


@auth.route('signup', methods=['GET','POST'])
def signup():
    # do something
    flash('Account created. Thank you for signing up.\nWelcome to Healthcare Insurance!')
    return render_template('user/signup.html')


@auth.route('login', methods=['GET', 'POST'])
def login():
    # do something
    flash('Welcome to Healthcare Insurance!')
    return render_template('user/login.html')


@auth.route('logout')
def logout():
    # do something
    flash('You have been logged out.')
    return render_template('index.html')
