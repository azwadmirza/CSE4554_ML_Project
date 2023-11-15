def returner(load):
    '''
    Return data to a postgres server
    '''
    conn = _get_conn()
    if conn is None:
        return None
    cur = conn.cursor()
    sql = '''INSERT INTO salt_returns
            (fun, jid, return, id, success)
            VALUES (%s, %s, %s, %s, %s)'''
    try:
        ret = six.text_type(load['return'])
    except UnicodeDecodeError:
        ret = str(load['return'])
    job_ret = {'return': ret}
    if 'retcode' in load:
        job_ret['retcode'] = load['retcode']
    if 'success' in load:
        job_ret['success'] = load['success']
    cur.execute(
        sql, (
            load['fun'],
            load['jid'],
            salt.utils.json.dumps(job_ret),
            load['id'],
            load.get('success'),
        )
    )
    _close_conn(conn)