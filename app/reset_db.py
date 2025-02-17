import pymysql
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

# Setup default values
insert_user_query = '''INSERT INTO user (role_id, first_name, last_name, email, password, encryption_key) VALUES (%s, %s, %s, %s, %s, %s)'''
default_hashed_password = generate_password_hash("12345678", method='pbkdf2:sha256')
default_owner = ('1', 'owner', 'account', 'owner@owner.owner', default_hashed_password, Fernet.generate_key().decode())
default_staff = ('2', 'staff', 'account', 'staff@staff.staff', default_hashed_password, Fernet.generate_key().decode())
default_customer = ('3', 'customer', 'account', 'customer@customer.customer', default_hashed_password, Fernet.generate_key().decode())
default_admin = ('4', 'admin', 'account', 'admin@admin.admin', default_hashed_password, Fernet.generate_key().decode())

try:
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        passwd="password123",
    )

    my_cursor = mydb.cursor()
    my_cursor.execute("USE website")
    my_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # Check and populate the roles table
    roles = ['Owner', 'Staff', 'Customer', 'Admin']
    for role in roles:
        my_cursor.execute("SELECT COUNT(*) FROM role WHERE name = %s", (role,))
        result = my_cursor.fetchone()
        if result[0] == 0:
            my_cursor.execute("INSERT INTO role (name) VALUES (%s)", (role,))

    # Check and add default users if they don't exist
    default_users = [
        ('owner@owner.owner', default_owner),
        ('staff@staff.staff', default_staff),
        ('customer@customer.customer', default_customer),
        ('admin@admin.admin', default_admin)
    ]

    for email, user_data in default_users:
        my_cursor.execute("SELECT COUNT(*) FROM user WHERE email = %s", (email,))
        if my_cursor.fetchone()[0] == 0:
            my_cursor.execute(insert_user_query, user_data)

    def encrypt_data(data, encryption_key):
        if encryption_key:
            cipher_suite = Fernet(encryption_key)
            cipher_text = cipher_suite.encrypt(data.encode())
            return cipher_text

    # Get encryption keys for existing users
    encryption_keys = {}
    for email in ['owner@owner.owner', 'staff@staff.staff', 'customer@customer.customer', 'admin@admin.admin']:
        my_cursor.execute("SELECT id, encryption_key FROM user WHERE email = %s", (email,))
        result = my_cursor.fetchone()
        if result:
            encryption_keys[email] = result[1]

    # Check and add billing addresses if they don't exist
    billing_addresses = [
        (1, "Owner", "owner@owner.owner", "123 Owner St", "OwnerCity", encrypt_data("10001", encryption_keys.get('owner@owner.owner')), "OwnerCountry", '2025-01-01 00:00:00'),
        (2, "Staff", "staff@staff.staff", "456 Staff Ave", "StaffCity", encrypt_data("20002", encryption_keys.get('staff@staff.staff')), "StaffCountry", '2025-01-01 00:00:00'),
        (3, "Customer", "customer@customer.customer", "789 Customer Blvd", "CustomerCity", encrypt_data("30003", encryption_keys.get('customer@customer.customer')), "CustomerCountry", '2025-01-01 00:00:00'),
        (4, "Admin", "admin@admin.admin", "321 Admin Rd", "AdminCity", encrypt_data("40004", encryption_keys.get('admin@admin.admin')), "AdminCountry", '2025-01-01 00:00:00')
    ]

    for address in billing_addresses:
        my_cursor.execute("SELECT COUNT(*) FROM billing_addresses WHERE user_id = %s", (address[0],))
        if my_cursor.fetchone()[0] == 0:
            my_cursor.execute("""
                INSERT INTO billing_addresses (user_id, fname, email, street_address, city, postal_code, country, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, address)

    # Check and add claims if they don't exist with proper ID tracking
    claims_general = [
        (1, "Owner", "owner@owner.owner", "POL001", "Accident Claim", '2025-01-10 10:00:00'),
        (2, "Staff", "staff@staff.staff", "POL002", "Health Claim", '2025-01-11 11:30:00'),
        (3, "Customer", "customer@customer.customer", "POL003", "Property Claim", '2025-01-12 14:45:00'),
        (4, "Admin", "admin@admin.admin", "POL004", "Travel Claim", '2025-01-13 16:15:00')
    ]

    # Dictionary to store IDs
    claim_ids = {
        'general': {},
        'specific': {}
    }

    # Insert general claims and track IDs
    for general in claims_general:
        user_id = general[0]
        policy_num = general[3]
        
        # Check if exists
        my_cursor.execute("SELECT id FROM Claims_General WHERE user_id = %s AND policy_num = %s", (user_id, policy_num))
        existing = my_cursor.fetchone()
        
        if existing:
            claim_ids['general'][user_id] = existing[0]
        else:
            my_cursor.execute("""
                INSERT INTO Claims_General (user_id, first_name, email, policy_num, reason_for_claim, date_of_claim)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, general)
            claim_ids['general'][user_id] = my_cursor.lastrowid

    # Insert specific claims and track IDs
    claims_specific = [
        (1, "Owner", "owner@owner.owner", "City Hospital", "New York", "receipt_owner.pdf"),
        (2, "Staff", "staff@staff.staff", "Health Clinic", "Los Angeles", "receipt_staff.pdf"), 
        (3, "Customer", "customer@customer.customer", "Property Repairs Inc.", "Chicago", "receipt_customer.pdf"),
        (4, "Admin", "admin@admin.admin", "Travel Medical Center", "Boston", "receipt_admin.pdf")
    ]

    for specific in claims_specific:
        user_id = specific[0]
        hospital = specific[3]
        
        # Check if exists
        my_cursor.execute("SELECT id FROM Claims_Specific WHERE user_id = %s AND hospital_name = %s", (user_id, hospital))
        existing = my_cursor.fetchone()
        
        if existing:
            claim_ids['specific'][user_id] = existing[0]
        else:
            my_cursor.execute("""
                INSERT INTO Claims_Specific (user_id, first_name, email, hospital_name, location, medical_receipts)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, specific)
            claim_ids['specific'][user_id] = my_cursor.lastrowid

    # Now insert claim metadata using tracked IDs
    claims_metadata = [
        (1, "Owner", "owner@owner.owner", "CLM001", claim_ids['general'][1], claim_ids['specific'][1], "In Progress"),
        (2, "Staff", "staff@staff.staff", "CLM002", claim_ids['general'][2], claim_ids['specific'][2], "In Progress"),
        (3, "Customer", "customer@customer.customer", "CLM003", claim_ids['general'][3], claim_ids['specific'][3], "In Progress"),
        (4, "Admin", "admin@admin.admin", "CLM004", claim_ids['general'][4], claim_ids['specific'][4], "In Progress")
    ]

    # Insert metadata with proper error handling
    for metadata in claims_metadata:
        try:
            my_cursor.execute("SELECT COUNT(*) FROM claim_metadata WHERE claim_num = %s", (metadata[3],))
            if my_cursor.fetchone()[0] == 0:
                my_cursor.execute("""
                    INSERT INTO claim_metadata 
                    (user_id, first_name, email, claim_num, general_id, specific_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, metadata)
                print(f"Added claim metadata for user {metadata[1]} with claim number {metadata[3]}")
        except Exception as e:
            print(f"Error inserting metadata for {metadata[3]}: {str(e)}")

    # Commit the transaction
    mydb.commit()

finally:
    if my_cursor:
        my_cursor.close()
    if mydb:
        mydb.close()