def list_principals():
    '''
    Get all principals

    CLI Example:

    .. code-block:: bash

        salt 'kde.example.com' kerberos.list_principals
    '''
    ret = {}

    cmd = __execute_kadmin('list_principals')

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    ret = {'principals': []}

    for i in cmd['stdout'].splitlines()[1:]:
        ret['principals'].append(i)

    return ret