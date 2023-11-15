def uptime(human_readable=True):
    '''
    Return the uptime for this minion

    human_readable: True
        If ``True`` return the output provided by the system.  If ``False``
        return the output in seconds.

        .. versionadded:: 2015.8.4

    CLI Example:

    .. code-block:: bash

        salt '*' status.uptime
    '''
    if human_readable:
        return __salt__['cmd.run']('uptime')
    else:
        if os.path.exists('/proc/uptime'):
            out = __salt__['cmd.run']('cat /proc/uptime').split()
            if len(out):
                return out[0]
            else:
                return 'unexpected format in /proc/uptime'
        return 'cannot find /proc/uptime'