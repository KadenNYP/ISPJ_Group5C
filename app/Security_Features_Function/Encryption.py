from cryptography.fernet import Fernet


def encrypt_data(data):
    from app.models import User
    from app.route import current_user

    EKey = User.query.filter_by(email=current_user.email).first()

    if EKey and EKey.encryption_Key:
        cipher_suite = Fernet(EKey.encryption_Key)
        cipher_text = cipher_suite.encrypt(data.encode())
        return cipher_text


def decrypt_data(encrypted_data):
    from app.models import User
    from app.route import current_user

    EKey = User.query.filter_by(email=current_user.email).first()

    if EKey and EKey.encryption_Key:
        cipher_suite = Fernet(EKey.encryption_Key)
        plain_text = cipher_suite.decrypt(encrypted_data).decode()
        return plain_text

