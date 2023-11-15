def osqueryd_monitor(configfile=None,
                     flagfile=None,
                     logdir=None,
                     databasepath=None,
                     pidfile=None,
                     hashfile=None,
                     daemonize=True):
    '''
    This function will monitor whether osqueryd is running on the system or not. 
    Whenever it detects that osqueryd is not running, it will start the osqueryd. 
    Also, it checks for conditions that would require osqueryd to restart(such as changes in flag file content) 
    On such conditions, osqueryd will get restarted, thereby loading new files.

    configfile
        Path to osquery configuration file.

    flagfile
        Path to osquery flag file

    logdir
        Path to log directory where osquery daemon/service will write logs

    pidfile
        pidfile path where osquery daemon will write pid info

    hashfile
        path to hashfile where osquery flagfile's hash would be stored

    daemonize
        daemonize osquery daemon. Default is True. Applicable for posix system only

    '''
    log.info("Starting osqueryd monitor")
    saltenv = __salt__['config.get']('hubblestack:nova:saltenv', 'base')
    osqueryd_path = 'salt://osquery'
    cached = __salt__['cp.cache_dir'](osqueryd_path, saltenv=saltenv)
    log.info('Cached osqueryd files to cachedir')
    cachedir = os.path.join(__opts__.get('cachedir'), 'files', saltenv, 'osquery')
    base_path = cachedir
    servicename = "hubble_osqueryd"
    if not logdir:
            logdir = __opts__.get('osquerylogpath')
    if not databasepath:
            databasepath = __opts__.get('osquery_dbpath')
    if salt.utils.platform.is_windows():
        if not pidfile:
            pidfile = os.path.join(base_path, "osqueryd.pidfile")
        if not configfile:
            configfile = os.path.join(base_path, "osquery.conf")
        if not flagfile:
            flagfile = os.path.join(base_path, "osquery.flags")
        if not hashfile:
            hashfile = os.path.join(base_path, "hash_of_flagfile.txt")

        osqueryd_running = _osqueryd_running_status_windows(servicename)
        if not osqueryd_running:
            _start_osqueryd(pidfile, configfile, flagfile, logdir, databasepath, servicename)
        else:
            osqueryd_restart = _osqueryd_restart_required(hashfile, flagfile)
            if osqueryd_restart:
                _restart_osqueryd(pidfile, configfile, flagfile, logdir, databasepath, hashfile, servicename)
    else:
        if not pidfile:
            pidfile = os.path.join(base_path, "osqueryd.pidfile")
        if not configfile:
            configfile = os.path.join(base_path, "osquery.conf")
        if not flagfile:
            flagfile = os.path.join(base_path, "osquery.flags")
        if not hashfile:
            hashfile = os.path.join(base_path, "hash_of_flagfile.txt")

        osqueryd_running = _osqueryd_running_status(pidfile, servicename)
        if not osqueryd_running:
            _start_osqueryd(pidfile, configfile, flagfile, logdir, databasepath, servicename)
        else:
            osqueryd_restart = _osqueryd_restart_required(hashfile, flagfile)
            if osqueryd_restart:
                _restart_osqueryd(pidfile, configfile, flagfile, logdir, databasepath, hashfile, servicename)