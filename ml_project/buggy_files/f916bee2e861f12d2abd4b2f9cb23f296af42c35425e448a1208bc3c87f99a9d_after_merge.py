def get_policy(name):
    '''
    Get policy details. Not supported by Heimdal backend.

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.get_policy my_policy
    '''
    ret = {}

    cmd = __execute_kadmin('get_policy {0}'.format(name))

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    for i in cmd['stdout'].splitlines()[1:]:
        (prop, val) = i.split(':', 1)

        ret[prop] = val

    return ret