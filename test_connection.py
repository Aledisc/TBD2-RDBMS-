import mysql.connector

print("Iniciando prueba...")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="tbd2_python",
        port=3306,
        connection_timeout=3
    )

    if conn.is_connected():
        print("Conexion exitosa")

except Exception as e:
    print("Error:", e)
