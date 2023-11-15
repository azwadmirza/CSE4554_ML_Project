def save_load(jid, load, minions=None):
    '''
    Save the load to the specified jid.
    '''
    write_profile = __opts__.get('etcd.returner_write_profile')
    client, path, ttl = _get_conn(__opts__, write_profile)

    # Check if the specified jid is 'req', as only incorrect code will do this
    if jid == 'req':
        log.debug('sdstack_etcd returner <save_load> was called using a request job id ({jid:s}) with {data:s}'.format(jid=jid, data=load))

    # Build the paths that we'll use for registration of our job
    loadp = '/'.join([path, Schema['job-cache'], jid, '.load.p'])
    lockp = '/'.join([path, Schema['job-cache'], jid, '.lock.p'])

    ## Now we can just store the current load
    json = salt.utils.json.dumps(load)

    log.debug('sdstack_etcd returner <save_load> storing load data for job {jid:s} to {path:s} with {data:s}'.format(jid=jid, path=loadp, data=load))
    try:
        res = client.write(loadp, json, prevExist=False)

    # If the key already exists, then warn the user and update the key. There
    # isn't anything we can really do about this because it's up to Salt really.
    except etcd.EtcdAlreadyExist as E:
        node = client.read(loadp)
        node.value = json

        log.debug('sdstack_etcd returner <save_load> updating load data for job {jid:s} at {path:s} with {data:s}'.format(jid=jid, path=loadp, data=load))
        res = client.update(node)

    # If we failed here, it's okay because the lock won't get written so this
    # essentially means the job will get scheduled for deletion.
    except Exception as E:
        log.trace("sdstack_etcd returner <save_load> unable to store load for job {jid:s} to the path {path:s} due to exception ({exception}) being raised".format(jid=jid, path=loadp, exception=E))
        return

    # Check if the previous node value and the current node value are different
    # so we can let the user know that something changed and that some data
    # might've been lost.
    try:
        if not res.newKey:
            d1, d2 = salt.utils.json.loads(res.value), salt.utils.json.loads(res._prev_node.value)
            j1, j2 = salt.utils.json.dumps(res.value, sort_keys=True), salt.utils.json.dumps(res._prev_node.value, sort_keys=True)
            if j1 != j2:
                log.warning("sdstack_etcd returner <save_load> overwrote the load data for job {jid:s} at {path:s} with {data:s}. Old data was {old:s}".format(jid=jid, path=res.key, data=d1, old=d2))
    except Exception as E:
        log.debug("sdstack_etcd returner <save_load> unable to compare load data for job {jid:s} at {path:s} due to exception ({exception}) being raised".format(jid=jid, path=loadp, exception=E))
        if not res.newKey:
            log.trace("sdstack_etcd returner <save_load> -- old load data for job {jid:s}: {data:s}".format(jid=jid, data=res._prev_node.value))
        log.trace("sdstack_etcd returner <save_load> -- new load data for job {jid:s}: {data:s}".format(jid=jid, data=res.value))

    # Since this is when a job is being created, create a lock that we can
    # check to see if the job has expired. This allows a user to signal to
    # salt that it's okay to remove the entire key by removing this lock.
    log.trace('sdstack_etcd returner <save_load> writing lock file for job {jid:s} at {path:s} using index {index:d}'.format(jid=jid, path=lockp, index=res.modifiedIndex))

    try:
        res = client.write(lockp, res.modifiedIndex, ttl=ttl if ttl > 0 else None)
        if res.ttl is not None:
            log.trace('sdstack_etcd returner <save_load> job {jid:s} at {path:s} will expire in {ttl:d} seconds'.format(jid=jid, path=res.key, ttl=res.ttl))

    except Exception as E:
        log.trace("sdstack_etcd returner <save_load> unable to write lock for job {jid:s} to the path {path:s} due to exception ({exception}) being raised".format(jid=jid, path=lockp, exception=E))

    return