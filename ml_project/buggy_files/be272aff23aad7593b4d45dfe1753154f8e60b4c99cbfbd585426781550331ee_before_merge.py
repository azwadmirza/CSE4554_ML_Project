def delete_principal(name):
    '''
    Delete Principal

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.delete_principal host/example.com@EXAMPLE.COM
    '''
    ret = {}

    cmd = __execute_kadmin('delprinc -force {0}'.format(name))

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    return True