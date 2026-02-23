def get_tables_and_views(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW FULL TABLES;")
    result = cursor.fetchall()

    tables = []
    views = []

    for row in result:
        name = row[0]
        table_type = row[1]

        if table_type == "BASE TABLE":
            tables.append(name)
        elif table_type == "VIEW":
            views.append(name)

    return tables, views

def get_procedures_and_functions(connection, database):

    cursor = connection.cursor()

    # Obtener procedures
    cursor.execute(
        f"SHOW PROCEDURE STATUS WHERE Db = '{database}';"
    )
    proc_result = cursor.fetchall()

    procedures = [row[1] for row in proc_result]

    # Obtener functions
    cursor.execute(
        f"SHOW FUNCTION STATUS WHERE Db = '{database}';"
    )
    func_result = cursor.fetchall()

    functions = [row[1] for row in func_result]

    return procedures, functions

def get_triggers(connection, database):
    cursor = connection.cursor()
    cursor.execute(f"SHOW TRIGGERS FROM {database};")
    result = cursor.fetchall()
    return [row[0] for row in result]

def get_indexes(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT INDEX_NAME
        FROM INFORMATION_SCHEMA.STATISTICS
    """)
    result = cursor.fetchall()
    return [row[0] for row in result]

def get_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM mysql.user;")
    result = cursor.fetchall()
    return [row[0] for row in result]