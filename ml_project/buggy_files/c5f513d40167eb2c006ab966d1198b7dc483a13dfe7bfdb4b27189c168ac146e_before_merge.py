def get_privs():
    '''
    Current privileges

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.get_privs
    '''
    ret = {}

    cmd = __execute_kadmin('get_privs')

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    for i in cmd['stdout'].splitlines()[1:]:
        (prop, val) = i.split(':', 1)

        ret[prop] = [j for j in val.split()]

    return ret