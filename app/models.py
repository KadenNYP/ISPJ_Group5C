from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from .init import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    lockout_time = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())

    def __init__(self, first_name, last_name, email, password, role):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role = role


class Encryption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    encryption_key = db.Column(db.String(50), nullable=False)

    def __init__(self, first_name, email, encryption_key):
        self.first_name = first_name
        self.email = email
        self.encryption_key = encryption_key


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(30), nullable=False)
    email = db.Column(db.VARCHAR(100), nullable=False)
    subject = db.Column(db.VARCHAR(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    anonymized_at = db.Column(db.TIMESTAMP, nullable=True)

    def __repr__(self):
        return f'<ContactMessage {self.name}>'
