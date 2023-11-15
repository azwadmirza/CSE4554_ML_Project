def multisave_sqlite(p, *vsheets):
    import sqlite3
    conn = sqlite3.connect(p.resolve())
    c = conn.cursor()

    for vs in vsheets:
        tblname = clean_to_id(vs.name)
        sqlcols = []
        for col in vs.visibleCols:
            sqlcols.append('%s %s' % (col.name, sqlite_type(col.type)))
        sql = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (tblname, ', '.join(sqlcols))
        c.execute(sql)

        for r in Progress(vs.rows, 'saving'):
            sqlvals = []
            for col in vs.visibleCols:
                sqlvals.append(col.getTypedValue(r))
            sql = 'INSERT INTO %s VALUES (%s)' % (tblname, ','.join(['?']*len(sqlvals)))
            c.execute(sql, sqlvals)

    conn.commit()

    status("%s save finished" % p)