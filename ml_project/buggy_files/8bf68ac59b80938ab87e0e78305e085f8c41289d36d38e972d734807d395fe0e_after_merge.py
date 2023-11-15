def upgrade(ver, session):
    if ver is None:
        # Upgrade to version 0 was a failed attempt at cleaning bad entries from our table, better attempt in ver 1
        ver = 0
    if ver == 0:
        try:
            # Remove any values that are not loadable.
            table = table_schema('simple_persistence', session)
            for row in session.execute(select([table.c.id, table.c.plugin, table.c.key, table.c.value])):
                try:
                    pickle.loads(row['value'])
                except Exception as e:
                    log.warning('Couldn\'t load %s:%s removing from db: %s' % (row['plugin'], row['key'], e))
                    session.execute(table.delete().where(table.c.id == row['id']))
        except Exception as e:
            log.warning('Couldn\'t upgrade the simple_persistence table. Commencing nuke. Error: %s', e)
            raise db_schema.UpgradeImpossible
        ver = 1
    if ver == 1:
        log.info('Creating index on simple_persistence table.')
        create_index('simple_persistence', session, 'feed', 'plugin', 'key')
        ver = 2
    if ver == 2 or ver == 3:
        table = table_schema('simple_persistence', session)
        table_add_column(table, 'json', Unicode, session)
        # Make sure we get the new schema with the added column
        table = table_schema('simple_persistence', session)
        failures = 0
        for row in session.execute(select([table.c.id, table.c.value])):
            try:
                p = pickle.loads(row['value'])
                session.execute(table.update().where(table.c.id == row['id']).values(
                    json=json.dumps(p, encode_datetime=True)))
            except Exception as e:
                failures += 1
        if failures > 0:
            log.error('Error upgrading %s simple_persistence pickle objects. Some information has been lost.', failures)
        ver = 4
    return ver