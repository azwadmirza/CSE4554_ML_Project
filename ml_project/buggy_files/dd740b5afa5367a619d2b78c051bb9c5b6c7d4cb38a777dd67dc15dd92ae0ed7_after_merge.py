def alter_db(name, character_set=None, collate=None, **connection_args):
    '''
    Modify database using ``ALTER DATABASE %(dbname)s CHARACTER SET %(charset)s
    COLLATE %(collation)s;`` query.

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.alter_db testdb charset='latin1'
    '''
    dbc = _connect(**connection_args)
    if dbc is None:
        return []
    cur = dbc.cursor()
    existing = db_get(name, **connection_args)
    qry = 'ALTER DATABASE `{0}` CHARACTER SET {1} COLLATE {2};'.format(
        name.replace('%', r'\%').replace('_', r'\_'),
        character_set or existing.get('character_set'),
        collate or existing.get('collate'))
    args = {}
    _execute(cur, qry, args)