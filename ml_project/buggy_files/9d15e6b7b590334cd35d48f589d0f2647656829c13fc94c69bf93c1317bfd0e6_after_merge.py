def query(database, query, **connection_args):
    '''
    Run an arbitrary SQL query and return the results or
    the number of affected rows.

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.query mydb "UPDATE mytable set myfield=1 limit 1"

    Return data:

    .. code-block:: python

        {'query time': {'human': '39.0ms', 'raw': '0.03899'}, 'rows affected': 1L}

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.query mydb "SELECT id,name,cash from users limit 3"

    Return data:

    .. code-block:: python

        {'columns': ('id', 'name', 'cash'),
            'query time': {'human': '1.0ms', 'raw': '0.001'},
            'results': ((1L, 'User 1', Decimal('110.000000')),
                        (2L, 'User 2', Decimal('215.636756')),
                        (3L, 'User 3', Decimal('0.040000'))),
            'rows returned': 3L}

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.query mydb 'INSERT into users values (null,"user 4", 5)'

    Return data:

    .. code-block:: python

        {'query time': {'human': '25.6ms', 'raw': '0.02563'}, 'rows affected': 1L}

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.query mydb 'DELETE from users where id = 4 limit 1'

    Return data:

    .. code-block:: python

        {'query time': {'human': '39.0ms', 'raw': '0.03899'}, 'rows affected': 1L}

    Jinja Example: Run a query on ``mydb`` and use row 0, column 0's data.

    .. code-block:: jinja

        {{ salt['mysql.query']('mydb', 'SELECT info from mytable limit 1')['results'][0][0] }}
    '''
    # Doesn't do anything about sql warnings, e.g. empty values on an insert.
    # I don't think it handles multiple queries at once, so adding "commit"
    # might not work.

    # The following 3 lines stops MySQLdb from converting the MySQL results
    # into Python objects. It leaves them as strings.
    orig_conv = MySQLdb.converters.conversions
    conv_iter = iter(orig_conv)
    conv = dict(zip(conv_iter, [str] * len(orig_conv)))

    # some converters are lists, do not break theses
    conv_mysqldb = {'MYSQLDB': True}
    if conv_mysqldb.get(MySQLdb.__package__.upper()):
        conv[FIELD_TYPE.BLOB] = [
            (FLAG.BINARY, str),
        ]
        conv[FIELD_TYPE.STRING] = [
            (FLAG.BINARY, str),
        ]
        conv[FIELD_TYPE.VAR_STRING] = [
            (FLAG.BINARY, str),
        ]
        conv[FIELD_TYPE.VARCHAR] = [
            (FLAG.BINARY, str),
        ]

    connection_args.update({'connection_db': database, 'connection_conv': conv})
    dbc = _connect(**connection_args)
    if dbc is None:
        return {}
    cur = dbc.cursor()
    start = time.time()
    log.debug('Using db: {0} to run query {1}'.format(database, query))
    try:
        affected = _execute(cur, query)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc)
        __context__['mysql.error'] = err
        log.error(err)
        return False
    results = cur.fetchall()
    elapsed = (time.time() - start)
    if elapsed < 0.200:
        elapsed_h = str(round(elapsed * 1000, 1)) + 'ms'
    else:
        elapsed_h = str(round(elapsed, 2)) + 's'

    ret = {}
    ret['query time'] = {'human': elapsed_h, 'raw': str(round(elapsed, 5))}
    select_keywords = ["SELECT", "SHOW", "DESC"]
    select_query = False
    for keyword in select_keywords:
        if query.upper().strip().startswith(keyword):
            select_query = True
            break
    if select_query:
        ret['rows returned'] = affected
        columns = ()
        for column in cur.description:
            columns += (column[0],)
        ret['columns'] = columns
        ret['results'] = results
        return ret
    else:
        ret['rows affected'] = affected
        return ret