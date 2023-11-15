def save_minions(jid, minions, syndic_id=None):  # pylint: disable=unused-argument
    '''
    Save/update the minion list for a given jid. The syndic_id argument is
    included for API compatibility only.
    '''
    write_profile = __opts__.get('etcd.returner_write_profile')
    client, path, _ = _get_conn(__opts__, write_profile)

    # Check if the specified jid is 'req', as only incorrect code will do that
    if jid == 'req':
        log.debug('sdstack_etcd returner <save_minions> was called with a request job id ({jid:s}) for minions {minions:s}'.format(jid=jid, minions=repr(minions)))

    # Figure out the path that our job should be at
    jobp = '/'.join([path, Schema['job-cache'], jid])
    loadp = '/'.join([jobp, '.load.p'])

    # Now we can try and read the load out of it.
    try:
        load = client.read(loadp)

    # If it doesn't exist, then bitch and complain because somebody lied to us
    except etcd.EtcdKeyNotFound as E:
        log.error('sdstack_etcd returner <save_minions> was called with an invalid job id ({jid:s}) for minions {minions:s}'.format(jid=jid, minions=repr(minions)))
        return

    log.debug('sdstack_etcd returner <save_minions> adding minions{syndics:s} for job {jid:s} to {path:s}'.format(jid=jid, path=jobp, syndics='' if syndic_id is None else ' from syndic {0}'.format(syndic_id)))

    # Iterate through all of the minions we received and update both the job
    # and minion-fun cache with what we know. Most of the other returners
    # don't do this, but it is definitely being called and is necessary for
    # syndics to actually work.
    exceptions = []
    for minion in minions:
        minionp = '/'.join([path, Schema['minion-fun'], minion])

        # Go ahead and write the job to the minion-fun cache and log if we've
        # overwritten an already existing job id.
        log.debug('sdstack_etcd returner <save_minions> writing (last) job id of {minion:s}{syndics:s} at {path:s} with job {jid:s}'.format(jid=jid, path=minionp, minion=minion, syndics='' if syndic_id is None else ' from syndic {0}'.format(syndic_id)))
        try:
            client.write(minionp, jid, ttl=load.ttl, prevExist=False)

        # If the minion already exists, then that's fine as we'll just update it
        # and move on.
        except etcd.EtcdAlreadyExist as E:
            node = client.read(minionp)

            log.debug('sdstack_etcd returner <save_minions> updating previous job id ({old:s}) of {minion:s}{syndics:s} at {path:s} with job {jid:s}'.format(old=node.value, minion=minion, jid=jid, path=node.key, syndics='' if syndic_id is None else ' from syndic {0}'.format(syndic_id)))

            node.value = jid
            client.update(node)

        except Exception as E:
            log.trace("sdstack_etcd returner <save_minions> unable to write job id {jid:s} for minion {minion:s} to {path:s} due to exception ({exception})".format(jid=jid, minion=minion, path=minionp, exception=E))
            exceptions.append((E, 'job', minion))

        # Now we can try and update the job. We don't have much, just the jid,
        # the minion, and the master id (syndic_id)
        resultp = '/'.join([jobp, minion])

        # One... (jid)
        try:
            res = client.write('/'.join([resultp, 'jid']), jid)

        except Exception as E:
            log.trace("sdstack_etcd returner <save_minions> unable to write job id {jid:s} to the result for the minion {minion:s} at {path:s} due to exception ({exception})".format(jid=jid, minion=minion, path='/'.join([resultp, 'jid']), exception=E))
            exceptions.append((E, 'result.jid', minion))

        # Two... (id)
        try:
            res = client.write('/'.join([resultp, 'id']), minion)

        except Exception as E:
            log.trace("sdstack_etcd returner <save_minions> unable to write minion id {minion:s} to the result for job {jid:s} at {path:s} due to exception ({exception})".format(jid=jid, minion=minion, path='/'.join([resultp, 'id']), exception=E))
            exceptions.append((E, 'result.id', minion))

        # Three... (master_id)
        try:
            if syndic_id is not None:
                res = client.write('/'.join([resultp, 'master_id']), syndic_id)

        except Exception as E:
            log.trace("sdstack_etcd returner <save_minions> unable to write master_id {syndic:s} to the result for job {jid:s} at {path:s} due to exception ({exception})".format(jid=jid, path='/'.join([resultp, 'master_id']), syndic=syndic_id, exception=E))
            exceptions.append((E, 'result.master_id', minion))

        # Crruuunch.

    # Go back through all the exceptions that occurred while trying to write the
    # fields and log them.
    for E, field, minion in exceptions:
        if field == 'job':
            log.exception("sdstack_etcd returner <save_minions> exception ({exception}) was raised while trying to update the function cache for minion {minion:s} to job {jid:s}".format(exception=E, minion=minion, jid=jid))
            continue
        log.exception("sdstack_etcd returner <save_minions> exception ({exception}) was raised while trying to update the {field:s} field in the result for job {jid:s} belonging to minion {minion:s}".format(exception=E, field=field, minion=minion, jid=jid))
    return