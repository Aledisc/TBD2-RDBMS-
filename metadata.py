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