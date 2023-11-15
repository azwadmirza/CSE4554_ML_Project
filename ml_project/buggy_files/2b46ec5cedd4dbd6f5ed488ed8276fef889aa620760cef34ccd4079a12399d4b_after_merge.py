def returner(ret):
    '''
    Return data to an etcd profile.
    '''
    write_profile = __opts__.get('etcd.returner_write_profile')
    client, path, ttl = _get_conn(__opts__, write_profile)

    # If a minion is returning a standalone job, update the jid for the load
    # when it's saved since this job came directly from a minion.
    if ret['jid'] == 'req':
        new_jid = prep_jid(nocache=ret.get('nocache', False))
        log.debug('sdstack_etcd returner <returner> satisfying a new job id request ({jid:s}) with id {new:s} for {data}'.format(jid=ret['jid'], new=new_jid, data=ret))
        ret['jid'] = new_jid
        save_load(new_jid, ret)

    # Update the given minion in the external job cache with the current (latest job)
    # This is used by get_fun() to return the last function that was called
    minionp = '/'.join([path, Schema['minion-fun'], ret['id']])

    # We can use the ttl here because our minionp is actually linked to the job
    # which will expire according to the ttl anyways..
    log.debug("sdstack_etcd returner <returner> updating (last) job id of {minion:s} at {path:s} with job {jid:s}".format(jid=ret['jid'], minion=ret['id'], path=minionp))
    res = client.write(minionp, ret['jid'], ttl=ttl if ttl > 0 else None)
    if not res.newKey:
        log.debug("sdstack_etcd returner <returner> the previous job id {old:s} for {minion:s} at {path:s} was set to {new:s}".format(old=res._prev_node.value, minion=ret['id'], path=minionp, new=res.value))

    # Figure out the path for the specified job and minion
    jobp = '/'.join([path, Schema['job-cache'], ret['jid'], ret['id']])
    log.debug("sdstack_etcd returner <returner> writing job data for {jid:s} to {path:s} with {data}".format(jid=ret['jid'], path=jobp, data=ret))

    # Iterate through all the fields in the return dict and dump them under the
    # jobs/$jid/id/$field key. We aggregate all the exceptions so that if an
    # error happens, the rest of the fields will still be written.
    exceptions = []
    for field in ret:
        fieldp = '/'.join([jobp, field])
        data = salt.utils.json.dumps(ret[field])
        try:
            res = client.write(fieldp, data)
        except Exception as E:
            log.trace("sdstack_etcd returner <returner> unable to set field {field:s} for job {jid:s} at {path:s} to {result} due to exception ({exception})".format(field=field, jid=ret['jid'], path=fieldp, result=ret[field], exception=E))
            exceptions.append((E, field, ret[field]))
            continue
        log.trace("sdstack_etcd returner <returner> set field {field:s} for job {jid:s} at {path:s} to {result}".format(field=field, jid=ret['jid'], path=res.key, result=ret[field]))

    # Go back through all the exceptions that occurred while trying to write the
    # fields and log them.
    for E, field, value in exceptions:
        log.exception("sdstack_etcd returner <returner> exception ({exception}) was raised while trying to set the field {field:s} for job {jid:s} to {value}".format(exception=E, field=field, jid=ret['jid'], value=value))
    return