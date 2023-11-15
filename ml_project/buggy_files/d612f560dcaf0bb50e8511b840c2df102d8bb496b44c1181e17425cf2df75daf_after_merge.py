def restart(name):
    '''
    Restart the named service

    CLI Example:

    .. code-block:: bash

        salt '*' service.restart <service name>
    '''
    stop(name)
    for idx in xrange(5):
        if status(name):
            time.sleep(2)
            continue
        return start(name)
    return False