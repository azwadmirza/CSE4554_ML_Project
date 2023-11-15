def processlist(**connection_args):
    '''
    Retrieves the processlist from the MySQL server via
    "SHOW FULL PROCESSLIST".

    Returns: a list of dicts, with each dict representing a process:
        {'Command': 'Query',
                          'Host': 'localhost',
                          'Id': 39,
                          'Info': 'SHOW FULL PROCESSLIST',
                          'Rows_examined': 0,
                          'Rows_read': 1,
                          'Rows_sent': 0,
                          'State': None,
                          'Time': 0,
                          'User': 'root',
                          'db': 'mysql'}

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.processlist

    '''
    ret = []

    dbc = _connect(**connection_args)
    if dbc is None:
        return []
    cur = dbc.cursor()
    _execute(cur, 'SHOW FULL PROCESSLIST')
    hdr = [c[0] for c in cur.description]
    for _ in range(cur.rowcount):
        row = cur.fetchone()
        idx_r = {}
        for idx_j in range(len(hdr)):
            idx_r[hdr[idx_j]] = row[idx_j]
        ret.append(idx_r)
    cur.close()
    return ret