def uptime(human_readable=False):
    '''
    .. versionadded:: 2015.8.0

    Return the system uptime for this machine in seconds

    human_readable : False
        If ``True``, then the number of seconds will be translated into years,
        months, days, etc.

    CLI Example:

    .. code-block:: bash

       salt '*' status.uptime
       salt '*' status.uptime human_readable=True
    '''

    # Open up a subprocess to get information from WMIC
    cmd = list2cmdline(['net', 'stats', 'srv'])
    outs = __salt__['cmd.run'](cmd)

    # Get the line that has when the computer started in it:
    stats_line = ''
    for line in outs.split('\r\n'):
        if "Statistics since" in line:
            stats_line = line

    # Extract the time string from the line and parse
    #
    # Get string
    startup_time = stats_line[len('Statistics Since '):]
    # Convert to struct
    startup_time = time.strptime(startup_time, '%d/%m/%Y %H:%M:%S')
    # eonvert to seconds since epoch
    startup_time = time.mktime(startup_time)

    # Subtract startup time from current time to get the uptime of the system
    uptime = time.time() - startup_time

    if human_readable:
        # Pull out the majority of the uptime tuple. h:m:s
        uptime = int(uptime)
        seconds = uptime % 60
        uptime /= 60
        minutes = uptime % 60
        uptime /= 60
        hours = uptime % 24
        uptime /= 24

        # Translate the h:m:s from above into HH:MM:SS format.
        ret = '{0:0>2}:{1:0>2}:{2:0>2}'.format(hours, minutes, seconds)

        # If the minion has been on for days, add that in.
        if uptime > 0:
            ret = 'Days: {0} {1}'.format(uptime % 365, ret)

        # If you have a Windows minion that has been up for years,
        # my hat is off to you sir.
        if uptime > 365:
            ret = 'Years: {0} {1}'.format(uptime / 365, ret)

        return ret

    else:
        return uptime