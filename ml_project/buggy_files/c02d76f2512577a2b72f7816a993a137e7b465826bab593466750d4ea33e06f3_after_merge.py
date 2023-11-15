def clean_old_jobs():
    '''
    Clean out minions's return data for old jobs.

    Normally, hset 'ret:<jid>' are saved with a TTL, and will eventually
    get cleaned by redis.But for jobs with some very late minion return, the
    corresponding hset's TTL will be refreshed to a too late timestamp, we'll
    do manually cleaning here.
    '''
    serv = _get_serv(ret=None)
    living_jids = set(serv.keys('load:*'))
    to_remove = []
    for ret_key in serv.keys('ret:*'):
        load_key = ret_key.replace('ret:', 'load:', 1)
        if load_key not in living_jids:
            to_remove.append(ret_key)
    serv.delete(*to_remove)