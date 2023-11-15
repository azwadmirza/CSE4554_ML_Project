def get_privs():
    '''
    Current privileges

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.get_privs
    '''
    ret = {}
    krb_flavor = __opts__.get('krb_flavor', None)
    if krb_flavor == "heimdal":
        krb_cmd = 'privileges'
    else:
        krb_cmd = 'get_privs'

    cmd = __execute_kadmin(krb_cmd)

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    if krb_flavor == "heimdal":
        ret["privileges"] = [i.strip() for i in cmd['stdout'].split(',')]

    else:
        for i in cmd['stdout'].splitlines()[1:]:
            (prop, val) = i.split(':', 1)

            ret[prop] = [j for j in val.split()]

    return ret