def handle_sqlite(sfile):
    """SQLite Dump - Readable Text"""
    logger.info("SQLite DB Extraction")
    try:
        data = ''
        con = sq.connect(sfile)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        for table in tables:
            data += "\nTABLE: " + table[0] + \
                " \n=====================================================\n"
            cur.execute("PRAGMA table_info('%s')" % table)
            rows = cur.fetchall()
            head = ''
            for sq_row in rows:
                elm_data = sq_row[1]
                head += elm_data + " | "
            data += head + " \n============================================" + \
                "=========================\n"
            cur.execute("SELECT * FROM '%s'" % table)
            rows = cur.fetchall()
            for sq_row in rows:
                dat = ''
                for each_row in sq_row:
                    dat += str(each_row) + " | "
                data += dat + "\n"
        return data
    except:
        PrintException("SQLite DB Extraction")