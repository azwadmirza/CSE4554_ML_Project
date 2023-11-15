def returner(ret):
    '''
    Return data to a mysql server
    '''
    try:
        with _get_serv(ret, commit=True) as cur:
            sql = '''INSERT INTO `salt_returns`
                    (`fun`, `jid`, `return`, `id`, `success`, `full_ret` )
                    VALUES (%s, %s, %s, %s, %s, %s)'''

            cur.execute(sql, (ret['fun'], ret['jid'],
                              json.dumps(ret['return']),
                              ret['id'],
                              ret['success'],
                              json.dumps(ret)))
    except salt.exceptions.SaltMasterError:
        log.critical('Could not store return with MySQL returner. MySQL server unavailable.')