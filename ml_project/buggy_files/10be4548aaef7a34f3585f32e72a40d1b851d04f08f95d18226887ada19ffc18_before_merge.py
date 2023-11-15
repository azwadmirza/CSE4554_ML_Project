def create_win_salt_restart_task():
    '''
    Create a task in Windows task scheduler to enable restarting the salt-minion

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt '*' service.create_win_salt_restart_task()
    '''
    cmd = 'cmd'
    args = '/c ping -n 3 127.0.0.1 && net stop salt-minion && net start ' \
           'salt-minion'
    return __salt__['task.create_task'](name='restart-salt-minion',
                                        user_name='System',
                                        force=True,
                                        action_type='Execute',
                                        cmd=cmd,
                                        arguments=args,
                                        trigger_type='Once',
                                        start_date='1975-01-01',
                                        start_time='01:00')