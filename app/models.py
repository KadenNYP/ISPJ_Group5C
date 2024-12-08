from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from .init import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    lockout_time = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(30), nullable=False)
    email = db.Column(db.VARCHAR(100), nullable=False)
    subject = db.Column(db.VARCHAR(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f'<ContactMessage {self.name}>'
