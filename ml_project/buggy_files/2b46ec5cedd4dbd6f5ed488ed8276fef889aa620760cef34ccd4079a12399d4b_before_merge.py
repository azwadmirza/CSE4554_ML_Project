def returner(ret):
    '''
    Return data to an etcd server or cluster
    '''
    write_profile = __opts__.get('etcd.returner_write_profile')
    if write_profile:
        ttl = __opts__.get(write_profile, {}).get('etcd.ttl')
    else:
        ttl = __opts__.get('etcd.ttl')

    client, path = _get_conn(__opts__, write_profile)
    # Make a note of this minion for the external job cache
    client.set(
        '/'.join((path, 'minions', ret['id'])),
        ret['jid'],
        ttl=ttl,
    )

    for field in ret:
        # Not using os.path.join because we're not dealing with file paths
        dest = '/'.join((
            path,
            'jobs',
            ret['jid'],
            ret['id'],
            field
        ))
        client.set(dest, salt.utils.json.dumps(ret[field]), ttl=ttl)