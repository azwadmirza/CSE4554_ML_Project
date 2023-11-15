def list_policies():
    '''
    List policies

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.list_policies
    '''
    ret = {}

    cmd = __execute_kadmin('list_policies')

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    ret = {'policies': []}

    for i in cmd['stdout'].splitlines()[1:]:
        ret['policies'].append(i)

    return ret