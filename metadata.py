def get_tables(connection, database_name):
    cursor = connection.cursor()
    query = """
        SELECT table_name
        FROM mysql.tables_priv
        WHERE db = %s
        GROUP BY table_name;
    """
    cursor.execute(query, (database_name,))
    result = cursor.fetchall()
    return [row[0] for row in result]