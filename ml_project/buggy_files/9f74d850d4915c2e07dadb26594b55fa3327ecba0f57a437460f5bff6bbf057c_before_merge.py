def beacon(config):
    '''
    Scan for processes and fire events

    Example Config

    .. code-block:: yaml

        beacons:
          ps:
            salt-master: running
            mysql: stopped

    The config above sets up beacons to check that
    processes are running or stopped.
    '''
    ret = []
    procs = []
    for proc in psutil.process_iter():
        _name = proc.name()
        if _name not in procs:
            procs.append(_name)

    for process in config:
        ret_dict = {}
        if config[process] == 'running':
            if process not in procs:
                ret_dict[process] = 'Stopped'
                ret.append(ret_dict)
        elif config[process] == 'stopped':
            if process in procs:
                ret_dict[process] = 'Running'
                ret.append(ret_dict)
        else:
            if process not in procs:
                ret_dict[process] = False
                ret.append(ret_dict)
    return ret