from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql import expression
from .init import db
from datetime import datetime


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    failed_login_attempts = db.Column(db.Integer, server_default=expression.text('0'), nullable=False)
    lockout_time = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())
    encryption_Key = db.Column(db.String(200), nullable=True)

    def __init__(self, first_name, last_name, email, password, role_id, encryption_key):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role_id = role_id
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    fname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())

    user = db.relationship('User', backref=db.backref('billing_addresses', lazy=True, passive_deletes=True))
    purchases = db.relationship('Purchase_details', backref='billing_address', lazy=True, passive_deletes=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    fname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(200), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)
    cvv = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())

    user = db.relationship('User', backref=db.backref('payments', lazy=True, passive_deletes=True))
    purchases = db.relationship('Purchase_details', backref='payment', lazy=True, passive_deletes=True)

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
    payment_method = db.Column(db.String(50))
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id', ondelete='CASCADE'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('billing_addresses.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"<Purchase {self.policy_num} - {self.first_name} - {self.effective_date}>"


class Claim_general_info(db.Model):
    __tablename__ = 'Claims_General'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    first_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    policy_num = db.Column(db.String(10), nullable=False)
    reason_for_claim = db.Column(db.String(255), nullable=False)
    date_of_claim = db.Column(db.TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    user = db.relationship('User', backref=db.backref('Claims_General', lazy=True, passive_deletes=True))


class Claim_specific_info(db.Model):
    __tablename__ = 'Claims_Specific'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    first_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    hospital_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    medical_receipts = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('Claims_Specific', lazy=True, passive_deletes=True))


class ClaimID(db.Model):
    __tablename__ = 'claim_metadata'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    first_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    claim_num = db.Column(db.String(10), unique=True, nullable=False)
    general_id = db.Column(db.Integer, db.ForeignKey('Claims_General.id', ondelete='CASCADE'), nullable=False)
    specific_id = db.Column(db.Integer, db.ForeignKey('Claims_Specific.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), default="In Progress")

    general_info = db.relationship('Claim_general_info', backref=db.backref('claim_metadata', lazy=True, passive_deletes=True))
    specific_info = db.relationship('Claim_specific_info', backref=db.backref('claim_metadata', lazy=True, passive_deletes=True))

class MedicalDocument(db.Model):
    __tablename__ = 'medical_documents'
    
    CLASSIFICATION_TYPES = ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED']
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now)
    document_type = db.Column(db.Enum(*CLASSIFICATION_TYPES, name='document_classification'), nullable=False, default='CONFIDENTIAL')
    expiry_date = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime)
    access_count = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='medical_documents')