def beacon(config):
    '''
    Return status for requested information
    '''
    log.debug(config)
    ctime = datetime.datetime.utcnow().isoformat()
    ret = {}
    if salt.utils.is_windows():
        return [{
            'tag': ctime,
            'data': ret,
        }]

    if len(config) < 1:
        config = [{
            'loadavg': ['all'],
            'cpustats': ['all'],
            'meminfo': ['all'],
            'vmstats': ['all'],
            'time': ['all'],
        }]

    if not isinstance(config, list):
        # To support the old dictionary config format
        config = [config]

    for entry in config:
        for func in entry:
            ret[func] = {}
            try:
                data = __salt__['status.{0}'.format(func)]()
            except salt.exceptions.CommandExecutionError as exc:
                log.debug('Status beacon attempted to process function {0} '
                          'but encountered error: {1}'.format(func, exc))
                continue
            if not isinstance(entry[func], list):
                func_items = [entry[func]]
            else:
                func_items = entry[func]
            for item in func_items:
                if item == 'all':
                    ret[func] = data
                else:
                    try:
                        try:
                            ret[func][item] = data[item]
                        except TypeError:
                            ret[func][item] = data[int(item)]
                    except KeyError as exc:
                        ret[func] = 'Status beacon is incorrectly configured: {0}'.format(exc)

    return [{
        'tag': ctime,
        'data': ret,
    }]