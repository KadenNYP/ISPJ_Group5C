from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from .init import db
from .Security_Features_Function.Encryption import *


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
    encryption_Key = db.Column(db.String(200), nullable=True)

    def __init__(self, first_name, last_name, email, password, role, encryption_key):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role = role
        self.encryption_Key = encryption_key


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


class BillingAddress(db.Model):
    __tablename__ = 'billing_addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())

    user = db.relationship('User', backref=db.backref('billing_addresses', lazy=True))

    def __init__(self, user_id, fname, email, street_address, city, postal_code, country, created_at):
        self.user_id = user_id
        self.fname = fname
        self.email = email
        self.street_address = street_address
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.created_at = created_at


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(200), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)
    cvv = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())

    user = db.relationship('User', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f"<Payment id={self.id} user_id={self.user_id}>"


class Purchase_details(db.Model):
    __tablename__ = 'purchase_detail'

    id = db.Column(db.Integer, primary_key=True)
    policy_num = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    plan_name = db.Column(db.String(20), nullable=False)
    plan_price = db.Column(db.String(20), nullable=False)
    effective_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Purchase {self.policy_num} - {self.first_name} - {self.effective_date}>"

