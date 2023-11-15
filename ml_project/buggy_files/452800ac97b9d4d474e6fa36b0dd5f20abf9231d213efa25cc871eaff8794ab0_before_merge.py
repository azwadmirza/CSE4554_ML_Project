def create(name, profile):
    '''
    Create the named vm

    CLI Example:

    .. code-block:: bash

        salt <minion-id> saltcloud.create webserver rackspace_centos_512
    '''
    cmd = 'salt-cloud --out json -p {0} {1}'.format(profile, name)
    out = __salt__['cmd.run_stdout'](cmd, python_shell=False)
    try:
        ret = salt.utils.json.loads(out, object_hook=salt.utils.data.encode_dict)
    except ValueError:
        ret = {}
    return ret