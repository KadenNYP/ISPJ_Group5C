import pymysql
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet



mydb = None
my_cursor = None
insert_user_query = '''INSERT INTO user (role_id, first_name, last_name, email, password, encryption_key) VALUES (%s, %s, %s, %s, %s, %s)'''
default_hashed_password = generate_password_hash("12345678", method='pbkdf2:sha256')
default_owner = ('1', 'owner', 'account', 'owner@owner.owner' , default_hashed_password, Fernet.generate_key().decode())
default_staff = ('2', 'staff', 'account', 'staff@staff.staff', default_hashed_password, Fernet.generate_key().decode())
default_customer = ('3', 'customer', 'account', 'customer@customer.customer', default_hashed_password, Fernet.generate_key().decode())

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
    roles = ['Owner', 'Staff', 'Customer']
    for role in roles:
        my_cursor.execute("SELECT COUNT(*) FROM role WHERE name = %s", (role,))
        result = my_cursor.fetchone()
        if result[0] == 0:
            my_cursor.execute("INSERT INTO role (name) VALUES (%s)", (role,))
    
    #delete the user table data
    my_cursor.execute("delete from user")

    # Reset auto-increment value
    my_cursor.execute("ALTER TABLE user AUTO_INCREMENT = 1")

    # Populate the user table
    my_cursor.execute(insert_user_query, default_owner)
    my_cursor.execute(insert_user_query, default_staff)
    my_cursor.execute(insert_user_query, default_customer)

    #delete the billing_addresses table data
    my_cursor.execute("delete from billing_addresses")

    def encrypt_data(data, encryption_key):

        EKey = encryption_key

        if EKey:
            cipher_suite = Fernet(EKey)
            cipher_text = cipher_suite.encrypt(data.encode())
            return cipher_text
        
    # Query encryption keys for each user
    my_cursor.execute("SELECT id, encryption_key FROM user WHERE email = 'owner@owner.owner'")
    owner_encryption_key = my_cursor.fetchone()[1]

    my_cursor.execute("SELECT id, encryption_key FROM user WHERE email = 'staff@staff.staff'")
    staff_encryption_key = my_cursor.fetchone()[1]

    my_cursor.execute("SELECT id, encryption_key FROM user WHERE email = 'customer@customer.customer'")
    customer_encryption_key = my_cursor.fetchone()[1]

    # Insert billing addresses for the three users
    billing_addresses = [
        (1, "Owner", "owner@owner.owner", "123 Owner St", "OwnerCity", encrypt_data("10001", owner_encryption_key), "OwnerCountry", '2025-01-01 00:00:00'),
        (2, "Staff", "staff@staff.staff", "456 Staff Ave", "StaffCity", encrypt_data("20002", staff_encryption_key), "StaffCountry", '2025-01-01 00:00:00'),
        (3, "Customer", "customer@customer.customer", "789 Customer Blvd", "CustomerCity", encrypt_data("30003", customer_encryption_key), "CustomerCountry", '2025-01-01 00:00:00')
    ]

    insert_billing_query = """
        INSERT INTO billing_addresses (user_id, fname, email, street_address, city, postal_code, country, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    for address in billing_addresses:
        my_cursor.execute(insert_billing_query, address)

    # Insert Claims_General entries for the three users
    claims_general = [
        (1, "Owner", "owner@owner.owner", "POL001", "Accident Claim", '2025-01-10 10:00:00'),
        (2, "Staff", "staff@staff.staff", "POL002", "Health Claim", '2025-01-11 11:30:00'),
        (3, "Customer", "customer@customer.customer", "POL003", "Property Claim", '2025-01-12 14:45:00')
    ]

    insert_claims_general_query = """
        INSERT INTO Claims_General (user_id, first_name, email, policy_num, reason_for_claim, date_of_claim)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    claim_general_ids = []
    for general in claims_general:
        my_cursor.execute(insert_claims_general_query, general)
        claim_general_ids.append(my_cursor.lastrowid)

    # Insert Claims_Specific entries for the three users
    claims_specific = [
        (1, "Owner", "owner@owner.owner", "City Hospital", "New York", "receipt_owner.pdf"),
        (2, "Staff", "staff@staff.staff", "Health Clinic", "Los Angeles", "receipt_staff.pdf"),
        (3, "Customer", "customer@customer.customer", "Property Repairs Inc.", "Chicago", "receipt_customer.pdf")
    ]

    insert_claims_specific_query = """
        INSERT INTO Claims_Specific (user_id, first_name, email, hospital_name, location, medical_receipts)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    claim_specific_ids = []
    for specific in claims_specific:
        my_cursor.execute(insert_claims_specific_query, specific)
        claim_specific_ids.append(my_cursor.lastrowid)

    # Insert claim_metadata entries linking Claims_General and Claims_Specific
    claims_metadata = [
        (1, "Owner", "owner@owner.owner", "CLM001", claim_general_ids[0], claim_specific_ids[0]),
        (2, "Staff", "staff@staff.staff", "CLM002", claim_general_ids[1], claim_specific_ids[1]),
        (3, "Customer", "customer@customer.customer", "CLM003", claim_general_ids[2], claim_specific_ids[2])
    ]

    insert_claim_metadata_query = """
        INSERT INTO claim_metadata (user_id, first_name, email, claim_num, general_id, specific_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for metadata in claims_metadata:
        my_cursor.execute(insert_claim_metadata_query, (*metadata, "In Progress"))

    # Commit the transaction
    mydb.commit()  

finally:
    if my_cursor:
        my_cursor.close()
    if mydb:
        mydb.close()