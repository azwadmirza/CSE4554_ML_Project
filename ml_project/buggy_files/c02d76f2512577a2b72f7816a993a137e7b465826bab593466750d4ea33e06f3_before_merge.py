def clean_old_jobs():
    '''
    Clean out minions's return data for old jobs.
    '''
    serv = _get_serv(ret=None)
    living_jids = set(serv.keys('load:*'))
    to_remove = []
    for ret_key in serv.keys('ret:*'):
        load_key = ret_key.replace('ret:', 'load:', 1)
        if load_key not in living_jids:
            to_remove.append(ret_key)
    serv.delete(**to_remove)  # pylint: disable=E1134