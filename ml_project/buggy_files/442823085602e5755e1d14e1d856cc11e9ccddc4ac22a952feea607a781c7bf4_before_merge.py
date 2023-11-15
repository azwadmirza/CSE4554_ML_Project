def read_sqlite(sqlite_file):
    """Read SQlite File"""
    try:
        logger.info("Dumping SQLITE Database")
        data = ''
        con = sqlite3.connect(sqlite_file)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        for table in tables:
            data += "\nTABLE: " + str(table[0]).decode('utf8', 'ignore') + \
                " \n=====================================================\n"
            cur.execute("PRAGMA table_info('%s')" % table)
            rows = cur.fetchall()
            head = ''
            for row in rows:
                head += str(row[1]).decode('utf8', 'ignore') + " | "
            data += head + " \n========================================" +\
                "=============================\n"
            cur.execute("SELECT * FROM '%s'" % table)
            rows = cur.fetchall()
            for row in rows:
                dat = ''
                for item in row:
                    dat += str(item).decode('utf8', 'ignore') + " | "
                data += dat + "\n"
        return data
    except:
        PrintException("[ERROR] Dumping SQLITE Database")