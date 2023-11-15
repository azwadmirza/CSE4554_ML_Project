def returner(ret):
    '''
    Insert minion return data into the sqlite3 database
    '''
    log.debug('sqlite3 returner <returner> called with data: {0}'.format(ret))
    conn = _get_conn()
    cur = conn.cursor()
    sql = '''INSERT INTO salt_returns
             (fun, jid, id, fun_args, date, full_ret, success)
             VALUES (:fun, :jid, :id, :fun_args, :date, :full_ret, :success)'''
    cur.execute(sql,
                {'fun': ret['fun'],
                 'jid': ret['jid'],
                 'id': ret['id'],
                 'fun_args': str(ret['fun_args']) if ret['fun_args'] else None,
                 'date': str(datetime.datetime.now()),
                 'full_ret': json.dumps(ret['return']),
                 'success': ret['success']})
    _close_conn(conn)