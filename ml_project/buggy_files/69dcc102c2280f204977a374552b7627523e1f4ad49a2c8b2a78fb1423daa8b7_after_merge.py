def get_load(jid):
    '''
    Return the load data that marks a specified jid.
    '''
    read_profile = __opts__.get('etcd.returner_read_profile')
    client, path, _ = _get_conn(__opts__, read_profile)

    # Figure out the path that our job should be at
    loadp = '/'.join([path, Schema['job-cache'], jid, '.load.p'])

    # Read it. If EtcdKeyNotFound was raised then the key doesn't exist and so
    # we need to return None, because that's what our caller expects on a
    # non-existent job.
    log.debug('sdstack_etcd returner <get_load> reading load data for job {jid:s} from {path:s}'.format(jid=jid, path=loadp))
    try:
        res = client.read(loadp)
    except etcd.EtcdKeyNotFound as E:
        log.error("sdstack_etcd returner <get_load> could not find job {jid:s} at the path {path:s}".format(jid=jid, path=loadp))
        return None
    log.debug('sdstack_etcd returner <get_load> found load data for job {jid:s} at {path:s} with value {data}'.format(jid=jid, path=res.key, data=res.value))
    return salt.utils.json.loads(res.value)