from cryptography.fernet import Fernet


def encrypt_data(data, user_id):
    from app.models import User

    EKey = User.query.filter_by(id=user_id).first()

    if EKey and EKey.encryption_Key:
        cipher_suite = Fernet(EKey.encryption_Key)
        # Only encode if data is not already bytes
        if not isinstance(data, bytes):
            data = data.encode()
        cipher_text = cipher_suite.encrypt(data)
        return cipher_text


def decrypt_data(encrypted_data, user_id):
    from app.models import User

    EKey = User.query.filter_by(id=user_id).first()

    if EKey and EKey.encryption_Key:
        cipher_suite = Fernet(EKey.encryption_Key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        # Only decode if we want string output
        if not isinstance(encrypted_data, bytes):
            return decrypted_data.decode()
        return decrypted_data

