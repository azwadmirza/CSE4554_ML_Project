def get_jids():
    '''
    Return a list of all job ids
    '''
    log.debug('sdstack_etcd returner <get_jids> called')
    ret = []
    client, path = _get_conn(__opts__)
    items = client.get('/'.join((path, 'jobs')))
    for item in items.children:
        if item.dir is True:
            jid = str(item.key).split('/')[-1]
            ret.append(jid)
    return ret