def store(bank, key, data):
    '''
    Store a key value.
    '''
    _init_client()
    data = __context__['serial'].dumps(data)
    query = b"REPLACE INTO {0} (bank, etcd_key, data) values('{1}', '{2}', " \
        b"'{3}')".format(_table_name,
                         bank,
                         key,
                         data)

    cur, cnt = run_query(client, query)
    cur.close()
    if cnt not in (1, 2):
        raise SaltCacheError(
            'Error storing {0} {1} returned {2}'.format(bank, key, cnt)
        )