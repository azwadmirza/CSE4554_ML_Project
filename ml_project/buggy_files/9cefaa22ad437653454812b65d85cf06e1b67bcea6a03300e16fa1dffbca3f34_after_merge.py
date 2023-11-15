def _get_conn(opts, profile=None):
    '''
    Establish a connection to an etcd profile.
    '''
    if profile is None:
        profile = opts.get('etcd.returner')

    # Grab the returner_root from the options
    path = opts.get('etcd.returner_root', '/salt/return')

    # Calculate the time-to-live for a job while giving etcd.ttl priority.
    # The etcd.ttl option specifies the number of seconds, whereas the keep_jobs
    # option specifies the number of hours. If any of these values are zero,
    # then jobs are forever persistent.

    ttl = opts.get('etcd.ttl', int(opts.get('keep_jobs', 0)) * 60 * 60)

    # Grab a connection using etcd_util, and then return the EtcdClient
    # from one of its attributes
    wrapper = salt.utils.etcd_util.get_conn(opts, profile)
    return wrapper.client, path, ttl