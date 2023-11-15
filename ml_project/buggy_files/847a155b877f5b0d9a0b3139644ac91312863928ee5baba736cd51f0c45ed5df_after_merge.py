def __grant_generate(grant,
                    database,
                    user,
                    host='localhost',
                    grant_option=False,
                    escape=True):
    # TODO: Re-order the grant so it is according to the
    #       SHOW GRANTS for xxx@yyy query (SELECT comes first, etc)
    grant = re.sub(r'\s*,\s*', ', ', grant).upper()

    # MySQL normalizes ALL to ALL PRIVILEGES, we do the same so that
    # grant_exists and grant_add ALL work correctly
    if grant == 'ALL':
        grant = 'ALL PRIVILEGES'

    db_part = database.rpartition('.')
    dbc = db_part[0]
    table = db_part[2]

    if escape:
        if dbc is not '*':
            dbc = '`{0}`'.format(dbc)
        if table is not '*':
            table = '`{0}`'.format(table)
    qry = 'GRANT {0} ON {1}.{2} TO {3!r}@{4!r}'.format(
        grant, dbc, table, user, host
    )
    if salt.utils.is_true(grant_option):
        qry += ' WITH GRANT OPTION'
    log.debug('Query generated: {0}'.format(qry))
    return qry