# Get databse connection.
# Uses os.getenv to read from a .env file for security. Or env when deplying with AWS.

import mysql.connector
import os
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host     = os.getenv("DB_HOST"),
            user     = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME"),
            connect_timeout = 10
        )
        print("Database connection successful")
        return connection
    except Error as e:
        print(f"Database connection failed: {e}")
        raise  # makes Flask return a 500 error
