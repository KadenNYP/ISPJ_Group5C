import pymysql
from werkzeug.security import generate_password_hash

mydb = None
my_cursor = None
insert_user_query = '''INSERT INTO user (role_id, first_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s)'''
default_hashed_password = generate_password_hash("12345678", method='pbkdf2:sha256')
default_customer = ('1', 'customer', 'customer', 'customer@customer.customer', default_hashed_password)
default_owner = ('2', 'owner', 'owner', 'owner@owner.owner' , default_hashed_password)
default_support = ('3', 'support', 'support', 'support@support.support', default_hashed_password)

try:
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        passwd="password123",
        )

    my_cursor = mydb.cursor()

    #Drop the database if it exists
    my_cursor.execute("DROP DATABASE IF EXISTS website")

    #Create the database
    my_cursor.execute("CREATE DATABASE website")

    my_cursor.execute("USE website")

    # Create the role table
    my_cursor.execute('''
    CREATE TABLE role (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
    );
    ''')

    # Populate the roles table
    my_cursor.execute('''
    INSERT INTO role (name) VALUES 
    ('Customer'),
    ('Owner'),
    ('Support');
    ''')

    # Create the user table
    my_cursor.execute('''
    CREATE TABLE user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        role_id INT DEFAULT 1,
        first_name VARCHAR(150) NOT NULL,
        last_name VARCHAR(150) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(150) NOT NULL,
        failed_login_attempts INT DEFAULT 0 NOT NULL,
        lockout_time DATETIME DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES role(id)
    );
    ''')

    # Populate the user table
    my_cursor.execute(insert_user_query, default_customer)
    my_cursor.execute(insert_user_query, default_owner)
    my_cursor.execute(insert_user_query, default_support)
    # Commit the transaction
    mydb.commit()  

finally:
    if my_cursor:
        my_cursor.close()
    if mydb:
        mydb.close()