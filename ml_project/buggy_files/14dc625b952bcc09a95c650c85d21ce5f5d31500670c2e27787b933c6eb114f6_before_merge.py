def get_fun(fun):
    '''
    Return a dict of the last function called for all minions
    '''
    log.debug('sdstack_etcd returner <get_fun> called fun: %s', fun)
    ret = {}
    client, path = _get_conn(__opts__)
    items = client.get('/'.join((path, 'minions')))
    for item in items.children:
        comps = str(item.key).split('/')
        efun = salt.utils.json.loads(client.get('/'.join((path, 'jobs', str(item.value), comps[-1], 'fun'))).value)
        if efun == fun:
            ret[comps[-1]] = str(efun)
    return ret