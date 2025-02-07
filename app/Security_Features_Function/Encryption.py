from cryptography.fernet import Fernet


def encrypt_data(data, user_id):
    from app.models import User

    EKey = User.query.filter_by(id=user_id).first()

    if EKey and EKey.encryption_Key:
        cipher_suite = Fernet(EKey.encryption_Key)
        cipher_text = cipher_suite.encrypt(data.encode())
        return cipher_text


def decrypt_data(encrypted_data, user_id):
    from app.models import User

    EKey = User.query.filter_by(id=user_id).first()

    if EKey and EKey.encryption_Key:
        cipher_suite = Fernet(EKey.encryption_Key)
        plain_text = cipher_suite.decrypt(encrypted_data).decode()
        return plain_text

