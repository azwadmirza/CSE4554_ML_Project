def get_principal(name):
    '''
    Get princial details

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.get_principal root/admin
    '''
    ret = {}
    krb_flavor = __opts__.get('krb_flavor', None)
    if krb_flavor == "heimdal":
        krb_cmd = 'get'
    else:
        krb_cmd = 'get_principals'

    cmd = __execute_kadmin(krb_cmd + ' {0}'.format(name))

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    for i in cmd['stdout'].splitlines()[1:]:
        (prop, val) = i.split(':', 1)

        ret[prop] = val

    return ret