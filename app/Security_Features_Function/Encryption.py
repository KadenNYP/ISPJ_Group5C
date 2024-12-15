from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os


def generate_user_key():
    key = os.urandom(32)
    return base64.urlsafe_b64encode(key).decode()


def encrypt_data(data, user_key):
    key = base64.urlsafe_b64decode(user_key)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted


def decrypt_data(encrypted_data, user_key):
    key = base64.urlsafe_b64decode(user_key)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data).decode()
    return decrypted
