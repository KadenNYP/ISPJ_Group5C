import pymysql

mydb = None
my_cursor = None

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

    my_cursor.execute('''
    CREATE TABLE user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(150) NOT NULL,
        last_name VARCHAR(150) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(150) NOT NULL,
        failed_login_attempts INT DEFAULT 0 NOT NULL,
        lockout_time DATETIME DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    ''')

finally:
    if my_cursor:
        my_cursor.close()
    if mydb:
        mydb.close()