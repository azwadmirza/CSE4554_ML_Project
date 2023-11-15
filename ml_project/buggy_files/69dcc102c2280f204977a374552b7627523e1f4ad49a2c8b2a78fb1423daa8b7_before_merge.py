def get_load(jid):
    '''
    Return the load data that marks a specified jid
    '''
    log.debug('sdstack_etcd returner <get_load> called jid: %s', jid)
    read_profile = __opts__.get('etcd.returner_read_profile')
    client, path = _get_conn(__opts__, read_profile)
    return salt.utils.json.loads(client.get('/'.join((path, 'jobs', jid, '.load.p'))).value)