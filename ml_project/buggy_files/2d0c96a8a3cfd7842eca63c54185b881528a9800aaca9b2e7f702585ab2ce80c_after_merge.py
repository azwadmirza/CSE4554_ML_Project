def get_minions():
    '''
    Return a list of all minions that have returned something.
    '''
    client, path, _ = _get_conn(__opts__)

    # Find any minions that have returned anything
    minionsp = '/'.join([path, Schema['minion-fun']])

    # If no minions were found, then nobody has returned anything recently. In
    # this case, return an empty last for the caller.
    log.debug('sdstack_etcd returner <get_minions> reading minions at {path:s}'.format(path=minionsp))
    try:
        minions = client.read(minionsp)
    except etcd.EtcdKeyNotFound as E:
        return []

    # We can just walk through everything that isn't a directory. This path
    # is simply a list of minions and the last job that each one returned.
    log.debug('sdstack_etcd returner <get_minions> iterating through minions at {path:s}'.format(path=minions.key))
    ret = []
    for minion in minions.leaves:
        if minion.dir:
            log.warning('sdstack_etcd returner <get_minions> found a non-minion at {path:s} {expire:s}'.format(path=minion.key, expire='that will need to be manually removed' if minion.ttl is None else 'that will expire in {ttl:d} seconds'.format(ttl=minion.ttl)))
            continue
        comps = str(minion.key).split('/')
        log.trace("sdstack_etcd returner <get_minions> found minion {minion:s} at {path:s}".format(minion=comps[-1], path=minion.key))
        ret.append(comps[-1])
    return ret