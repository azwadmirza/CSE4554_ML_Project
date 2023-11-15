def list_principals():
    '''
    Get all principals

    CLI Example:

    .. code-block:: bash

        salt 'kde.example.com' kerberos.list_principals
    '''
    ret = {}
    krb_flavor = __opts__.get('krb_flavor', None)
    if krb_flavor == "heimdal":
        krb_cmd = 'get -t "*"'
    else:
        krb_cmd = 'list_principals'

    cmd = __execute_kadmin(krb_cmd)

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    ret = {'principals': []}

    for i in cmd['stdout'].splitlines()[1:]:
        ret['principals'].append(i)

    return ret