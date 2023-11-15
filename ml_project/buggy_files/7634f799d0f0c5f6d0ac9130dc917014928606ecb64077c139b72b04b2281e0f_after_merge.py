def set_computer_desc(desc):
    '''
    Set the Windows computer description

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' system.set_computer_desc 'This computer belongs to Dave!'
    '''
    cmd = 'net config server /srvcomment:"{0}"'.format(desc)
    __salt__['cmd.run'](cmd)
    return {'Computer Description': get_computer_desc()}