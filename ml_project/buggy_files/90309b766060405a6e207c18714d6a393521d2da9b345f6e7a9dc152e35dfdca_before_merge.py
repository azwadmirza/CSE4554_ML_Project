def new_db_version_ok(new_database_path):
    # Let's check if we converted all/some entries before
    connection = sqlite3.connect(new_database_path)
    with connection:
        cursor = connection.cursor()
        cursor.execute('SELECT value FROM MiscData WHERE name == "db_version"')
        version = int(cursor.fetchone()[0])
        if version != 0:
            return False
    connection.close()
    return True