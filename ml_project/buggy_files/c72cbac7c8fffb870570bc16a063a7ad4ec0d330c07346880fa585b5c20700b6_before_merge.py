def returner(ret):
    '''
    Return data to a mysql server
    '''
    with _get_serv(ret, commit=True) as cur:
        sql = '''INSERT INTO `salt_returns`
                (`fun`, `jid`, `return`, `id`, `success`, `full_ret` )
                VALUES (%s, %s, %s, %s, %s, %s)'''

        cur.execute(sql, (ret['fun'], ret['jid'],
                          json.dumps(ret['return']),
                          ret['id'],
                          ret['success'],
                          json.dumps(ret)))