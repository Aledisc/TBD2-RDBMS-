import mysql.connector
from mysql.connector import Error as MySQLError

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

def create_slave_connection(host, user, password, database):

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            connection_timeout=5
        )
        if conn.is_connected():
            return conn
    except MySQLError as e:
        print("Error conectando a MySQL (SLAVE):", e)
    return None


def create_master_connection(host, user, password, database, port=5432):
    if not PSYCOPG2_AVAILABLE:
        print("psycopg2 no instalado. Ejecuta: pip install psycopg2-binary")
        return None
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=database,
            port=port,
            connect_timeout=5
        )
        return conn
    except Exception as e:
        print("Error conectando a PostgreSQL (MASTER):", e)
    return None

def create_connection(host, user, password, database):
    return create_slave_connection(host, user, password, database)
