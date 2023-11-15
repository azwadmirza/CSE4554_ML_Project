def get_jid(jid):
    '''
    Return the information returned when the specified job id was executed.
    '''
    client, path, _ = _get_conn(__opts__)

    # Figure out the path that our job should be at
    resultsp = '/'.join([path, Schema['job-cache'], jid])

    # Try and read the job directory. If we have a missing key exception then no
    # minions have returned anything yet and so we return an empty dict for the
    # caller.
    log.debug('sdstack_etcd returner <get_jid> reading minions that have returned results for job {jid:s} at {path:s}'.format(jid=jid, path=resultsp))
    try:
        results = client.read(resultsp)
    except etcd.EtcdKeyNotFound as E:
        log.trace('sdstack_etcd returner <get_jid> unable to read job {jid:s} from {path:s}'.format(jid=jid, path=resultsp))
        return {}

    # Iterate through all of the children at our job path that are directories.
    # Anything that is a directory should be a minion that contains some results.
    log.debug('sdstack_etcd returner <get_jid> iterating through minions with results for job {jid:s} from {path:s}'.format(jid=results.key.split('/')[-1], path=results.key))
    ret = {}
    for item in results.leaves:
        if not item.dir:
            continue

        # Extract the minion name from the key in the job, and use it to build
        # the path to the return value
        comps = item.key.split('/')
        returnp = '/'.join([resultsp, comps[-1], 'return'])

        # Now we know the minion and the path to the return for its job, we can
        # just grab it. If the key exists, but the value is missing entirely,
        # then something that shouldn't happen has happened.
        log.trace('sdstack_etcd returner <get_jid> grabbing result from minion {minion:s} for job {jid:s} at {path:s}'.format(minion=comps[-1], jid=jid, path=returnp))
        try:
            result = client.read(returnp, recursive=True)
        except etcd.EtcdKeyNotFound as E:
            log.debug("sdstack_etcd returner <get_jid> returned nothing from minion {minion:s} for job {jid:s} at {path:s}".format(minion=comps[-1], jid=jid, path=returnp))
            continue

        # Aggregate any keys that we found into a dictionary
        res = {}
        for item in result.leaves:
            name = item.key.split('/')[-1]
            try:
                res[name] = salt.utils.json.loads(item.value)

            # We use a general exception here instead of ValueError jic someone
            # changes the semantics of salt.utils.json.loads out from underneath us
            except Exception as E:
                log.warning("sdstack_etcd returner <get_jid> unable to decode field {name:s} from minion {minion:s} for job {jid:s} at {path:s}".format(minion=comps[-1], jid=jid, path=item.key, name=name))
                res[name] = item.value
            continue

        # We found something, so update our return dict for the minion id with
        # the results that it returned.
        ret[comps[-1]] = res
        log.debug("sdstack_etcd returner <get_jid> job {jid:s} from minion {minion:s} at path {path:s} returned {result}".format(minion=comps[-1], jid=jid, path=result.key, result=res))
    return ret