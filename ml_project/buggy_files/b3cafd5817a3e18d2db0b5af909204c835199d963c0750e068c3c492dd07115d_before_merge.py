def hash_known_hosts(user=None, config=None):
    '''

    Hash all the hostnames in the known hosts file.

    .. versionadded:: 2014.7.0

    user
        hash known hosts of this user

    config
        path to known hosts file: can be absolute or relative to user's home
        directory

    CLI Example:

    .. code-block:: bash

        salt '*' ssh.hash_known_hosts

    '''
    full = _get_known_hosts_file(config=config, user=user)

    if isinstance(full, dict):
        return full  # full contains error information

    if not os.path.isfile(full):
        return {'status': 'error',
                'error': 'Known hosts file {0} does not exist'.format(full)}
    origmode = os.stat(full).st_mode
    cmd = ['ssh-keygen', '-H', '-f', full]
    cmd_result = __salt__['cmd.run'](cmd, python_shell=False)
    os.stat(full, origmode)
    # ssh-keygen creates a new file, thus a chown is required.
    if os.geteuid() == 0 and user:
        uinfo = __salt__['user.info'](user)
        os.chown(full, uinfo['uid'], uinfo['gid'])
    return {'status': 'updated', 'comment': cmd_result}