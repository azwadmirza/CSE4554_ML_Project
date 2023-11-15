def save_load(jid, load, minions=None):
    '''
    Save the load to the specified jid
    '''
    log.debug('sdstack_etcd returner <save_load> called jid: %s', jid)
    write_profile = __opts__.get('etcd.returner_write_profile')
    client, path = _get_conn(__opts__, write_profile)
    if write_profile:
        ttl = __opts__.get(write_profile, {}).get('etcd.ttl')
    else:
        ttl = __opts__.get('etcd.ttl')
    client.set(
        '/'.join((path, 'jobs', jid, '.load.p')),
        salt.utils.json.dumps(load),
        ttl=ttl,
    )