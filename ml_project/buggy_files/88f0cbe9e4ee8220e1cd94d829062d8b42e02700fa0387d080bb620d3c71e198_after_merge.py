def get_jids():
    '''
    Return a list of all job ids that have returned something.
    '''
    client, path, _ = _get_conn(__opts__)

    # Enumerate all the jobs that are available.
    jobsp = '/'.join([path, Schema['job-cache']])

    # Fetch all the jobs. If the key doesn't exist, then it's likely that no
    # jobs have been created yet so return an empty list to the caller.
    log.debug("sdstack_etcd returner <get_jids> listing jobs at {path:s}".format(path=jobsp))
    try:
        jobs = client.read(jobsp)
    except etcd.EtcdKeyNotFound as E:
        return []

    # Anything that's a directory is a job id. Since that's all we're returning,
    # aggregate them into a list.
    log.debug("sdstack_etcd returner <get_jids> iterating through jobs at {path:s}".format(path=jobs.key))
    ret = {}
    for job in jobs.leaves:
        if not job.dir:
            log.warning('sdstack_etcd returner <get_jids> found a non-job at {path:s} {expire:s}'.format(path=job.key, expire='that will need to be manually removed' if job.ttl is None else 'that will expire in {ttl:d} seconds'.format(ttl=job.ttl)))
            continue

        jid = job.key.split('/')[-1]
        loadp = '/'.join([job.key, '.load.p'])

        # Now we can load the data from the job
        try:
            res = client.read(loadp)
        except etcd.EtcdKeyNotFound as E:
            log.error("sdstack_etcd returner <get_jids> could not find job data {jid:s} at the path {path:s}".format(jid=jid, path=loadp))
            continue

        # Decode the load data so we can stash the job data for our caller
        try:
            data = salt.utils.json.loads(res.value)

        # If we can't decode the json, then we're screwed so log it in case the user cares
        except Exception as E:
            log.error("sdstack_etcd returner <get_jids> could not decode data for job {jid:s} at the path {path:s} due to exception ({exception}) being raised. Data was {data:s}".format(jid=jid, path=loadp, exception=E, data=res.value))
            continue

        # Cool. Everything seems to be good...
        ret[jid] = salt.utils.jid.format_jid_instance(jid, data)
        log.trace("sdstack_etcd returner <get_jids> found job {jid:s} at {path:s}".format(jid=jid, path=job.key))

    log.debug("sdstack_etcd returner <get_jids> found {count:d} jobs at {path:s}".format(count=len(ret), path=jobs.key))
    return ret