def cleanup_pony_experimental_db(new_database_path):
    # Check for the old experimental version database
    # ACHTUNG!!! NUCLEAR OPTION!!! DO NOT MESS WITH IT!!!
    connection = sqlite3.connect(new_database_path)
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'MiscData'")
        result = cursor.fetchone()
        delete_old_pony_db = not bool(result[0] if result else False)
        if not delete_old_pony_db:
            cursor.execute('SELECT value FROM MiscData WHERE name == "db_version"')
            version = int(cursor.fetchone()[0])
            delete_old_pony_db = version in BETA_DB_VERSIONS  # Delete the older betas DB
    connection.close()
    # We're looking at the old experimental version database. Delete it.
    if delete_old_pony_db:
        os.unlink(new_database_path)