# Used for connecting to a databse, in seperat file so that you would have the option to .gitignroe it.

import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL_Pass654321",
        database="database"
    )
    return connection
