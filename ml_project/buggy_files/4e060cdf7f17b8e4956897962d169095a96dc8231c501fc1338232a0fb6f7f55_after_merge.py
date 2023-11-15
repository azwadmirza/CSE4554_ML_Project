def clean_old_jobs():
    '''
    Called in the master's event loop every loop_interval. Removes any jobs,
    and returns that are older than the etcd.ttl option (seconds), or the
    keep_jobs option (hours).

    :return:
    '''

    # First we'll purge the jobs...
    jobc = _purge_jobs()
    if jobc > 0:
        log.trace('sdstack_etcd returner <clean_old_jobs> successfully removed {count:d} jobs'.format(count=jobc))

    # ...and then we'll purge the events
    eventsc = _purge_events()
    if eventsc > 0:
        log.trace('sdstack_etcd returner <clean_old_jobs> successfully removed {count:d} events'.format(count=eventsc))

    # Log that we hit a cleanup iteration
    log.debug('sdstack_etcd returner <clean_old_jobs> completed purging jobs and events')