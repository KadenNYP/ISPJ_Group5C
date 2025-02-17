from datetime import datetime, timedelta

def check_document_access(classification_type, user):
    """Define access rules for different document classifications"""
    access_matrix = {
        'PUBLIC': ['user', 'staff', 'admin'],
        'INTERNAL': ['staff', 'admin'],
        'CONFIDENTIAL': ['staff', 'admin'],
        'RESTRICTED': ['admin']
    }
    return user.role.name.lower() in access_matrix.get(classification_type.upper(), [])

def get_document_expiry(classification_type):
    """Define expiry periods for different classifications"""
    expiry_periods = {
        'PUBLIC': timedelta(days=365),
        'INTERNAL': timedelta(days=180),
        'CONFIDENTIAL': timedelta(days=90),
        'RESTRICTED': timedelta(days=30)
    }
    return datetime.now() + expiry_periods.get(classification_type.upper(), timedelta(days=90))
