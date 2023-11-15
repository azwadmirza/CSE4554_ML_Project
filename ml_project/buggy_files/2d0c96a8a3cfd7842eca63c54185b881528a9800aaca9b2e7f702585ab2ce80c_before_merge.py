def get_minions():
    '''
    Return a list of minions
    '''
    log.debug('sdstack_etcd returner <get_minions> called')
    ret = []
    client, path = _get_conn(__opts__)
    items = client.get('/'.join((path, 'minions')))
    for item in items.children:
        comps = str(item.key).split('/')
        ret.append(comps[-1])
    return ret