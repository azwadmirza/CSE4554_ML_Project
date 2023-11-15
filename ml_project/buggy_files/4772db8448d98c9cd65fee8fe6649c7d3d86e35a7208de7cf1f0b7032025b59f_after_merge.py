def uptime():
    '''
    Return the uptime for this system.

    CLI Example:

    .. code-block:: bash

        salt '*' status.uptime
    '''
    ut_path = "/proc/uptime"
    if not os.path.exists(ut_path):
        raise CommandExecutionError("File {ut_path} was not found.".format(ut_path=ut_path))

    ut_ret = {
        'seconds': int(float(open(ut_path).read().strip().split()[0]))
    }

    utc_time = datetime.datetime.utcfromtimestamp(time.time() - ut_ret['seconds'])
    ut_ret['since_iso'] = utc_time.isoformat()
    ut_ret['since_t'] = time.mktime(utc_time.timetuple())
    ut_ret['days'] = ut_ret['seconds'] / 60 / 60 / 24
    hours = (ut_ret['seconds'] - (ut_ret['days'] * 24 * 60 * 60)) / 60 / 60
    minutes = ((ut_ret['seconds'] - (ut_ret['days'] * 24 * 60 * 60)) / 60) - hours * 60
    ut_ret['time'] = '{0}:{1}'.format(hours, minutes)
    ut_ret['users'] = len(__salt__['cmd.run']("who -s").split(os.linesep))

    return ut_ret