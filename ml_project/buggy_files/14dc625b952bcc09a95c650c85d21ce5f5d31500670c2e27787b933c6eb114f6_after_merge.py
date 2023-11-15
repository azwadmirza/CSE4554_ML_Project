def get_fun(fun):
    '''
    Return a dict containing the last function called for all the minions that have called a function.
    '''
    client, path, _ = _get_conn(__opts__)

    # Find any minions that had their last function registered by returner()
    minionsp = '/'.join([path, Schema['minion-fun']])

    # If the minions key isn't found, then no minions registered a function
    # and thus we need to return an empty dict so the caller knows that
    # nothing is available.
    log.debug('sdstack_etcd returner <get_fun> reading minions at {path:s} for function {fun:s}'.format(path=minionsp, fun=fun))
    try:
        minions = client.read(minionsp)
    except etcd.EtcdKeyNotFound as E:
        return {}

    # Walk through the list of all the minions that have a jid registered,
    # and cross reference this with the job returns.
    log.debug('sdstack_etcd returner <get_fun> iterating through minions for function {fun:s} at {path:s}'.format(fun=fun, path=minions.key))
    ret = {}
    for minion in minions.leaves:
        if minion.dir:
            log.warning('sdstack_etcd returner <get_fun> found a non-minion at {path:s} {expire:s}'.format(path=minion.key, expire='that will need to be manually removed' if minion.ttl is None else 'that will expire in {ttl:d} seconds'.format(ttl=minion.ttl)))
            continue

        # Now that we have a minion and it's last jid, we use it to fetch the
        # function field (fun) that was registered by returner().
        jid, comps = minion.value, minion.key.split('/')
        funp = '/'.join([path, Schema['job-cache'], jid, comps[-1], 'fun'])

        # Try and read the field, and skip it if it doesn't exist or wasn't
        # registered for some reason.
        log.trace('sdstack_etcd returner <get_fun> reading function from minion {minion:s} for job {jid:s} at {path:s}'.format(minion=comps[-1], jid=jid, path=funp))
        try:
            res = client.read(funp)
        except etcd.EtcdKeyNotFound as E:
            log.debug("sdstack_etcd returner <get_fun> returned nothing from minion {minion:s} for job {jid:s} at path {path:s}".format(minion=comps[-1], jid=jid, path=funp))
            continue

        # Check if the function field (fun) matches what the user is looking for
        # If it does, then we can just add the minion to our results
        log.trace('sdstack_etcd returner <get_fun> decoding json data from minion {minion:s} for job {jid:s} at {path:s}'.format(minion=comps[-1], jid=jid, path=funp))
        data = salt.utils.json.loads(res.value)
        if data == fun:
            ret[comps[-1]] = str(data)
            log.debug("sdstack_etcd returner <get_fun> found job {jid:s} for minion {minion:s} using {fun:s} at {path:s}".format(minion=comps[-1], fun=data, jid=jid, path=minion.key))
        continue
    return ret