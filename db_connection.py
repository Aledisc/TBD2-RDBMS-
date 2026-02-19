import mysql.connector
from mysql.connector import Error

def create_connection(host, user, password, database):
    try:

        connection = mysql.connector.connect(


            host=host,
            user="root",
            password=password,
            database=database,
            connection_timeout=5
        )


        if connection.is_connected():
            return connection

    except Error as e:
        print("Error conenctando a MySQL:", e)
        return None
