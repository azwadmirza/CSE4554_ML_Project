def get_jid(jid):
    '''
    Return the information returned when the specified job id was executed
    '''
    log.debug('sdstack_etcd returner <get_jid> called jid: %s', jid)
    ret = {}
    client, path = _get_conn(__opts__)
    items = client.get('/'.join((path, 'jobs', jid)))
    for item in items.children:
        if str(item.key).endswith('.load.p'):
            continue
        comps = str(item.key).split('/')
        data = client.get('/'.join((path, 'jobs', jid, comps[-1], 'return'))).value
        ret[comps[-1]] = {'return': salt.utils.json.loads(data)}
    return ret