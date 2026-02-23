def get_tables(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    result = cursor.fetchall()
    return [row[0] for row in result]