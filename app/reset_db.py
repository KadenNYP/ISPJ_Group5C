import pymysql
from werkzeug.security import generate_password_hash
from Security_Features_Function.Encryption import *

mydb = None
my_cursor = None
encryption_key = Fernet.generate_key().decode()
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

    # Insert billing addresses for the three users
    billing_addresses = [
        (1, "Owner", "owner@owner.owner", "123 Owner St", "OwnerCity", "10001", "OwnerCountry", '2025-01-01 00:00:00'),
        (2, "Staff", "staff@staff.staff", "456 Staff Ave", "StaffCity", "20002", "StaffCountry", '2025-01-01 00:00:00'),
        (3, "Customer", "customer@customer.customer", "789 Customer Blvd", "CustomerCity", "30003", "CustomerCountry", '2025-01-01 00:00:00')
    ]

    insert_billing_query = """
        INSERT INTO billing_addresses (user_id, fname, email, street_address, city, postal_code, country, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    for address in billing_addresses:
        my_cursor.execute(insert_billing_query, address)

    # Commit the transaction
    mydb.commit()  

finally:
    if my_cursor:
        my_cursor.close()
    if mydb:
        mydb.close()