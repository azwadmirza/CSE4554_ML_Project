def migrate():
    if not engine.dialect.has_table(engine.connect(), "permissions_added"):
        PermissionAdded.__table__.create(bind = engine)
    for sql in session.execute("select sql from sqlite_master where type='table'"):
        if 'CREATE TABLE gdrive_ids' in sql[0]:
            currUniqueConstraint = 'UNIQUE (gdrive_id)'
            if currUniqueConstraint in sql[0]:
                sql=sql[0].replace(currUniqueConstraint, 'UNIQUE (gdrive_id, path)')
                sql=sql.replace(GdriveId.__tablename__, GdriveId.__tablename__ + '2')
                session.execute(sql)
                session.execute("INSERT INTO gdrive_ids2 (id, gdrive_id, path) SELECT id, "
                                "gdrive_id, path FROM gdrive_ids;")
                session.commit()
                session.execute('DROP TABLE %s' % 'gdrive_ids')
                session.execute('ALTER TABLE gdrive_ids2 RENAME to gdrive_ids')
            break