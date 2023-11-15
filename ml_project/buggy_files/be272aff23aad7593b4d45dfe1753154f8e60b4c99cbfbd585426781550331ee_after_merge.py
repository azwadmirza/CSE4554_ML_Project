def delete_principal(name):
    '''
    Delete Principal

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.delete_principal host/example.com@EXAMPLE.COM
    '''
    ret = {}
    krb_flavor = __opts__.get('krb_flavor', None)
    if krb_flavor == "heimdal":
        krb_cmd = 'delete'
    else:
        krb_cmd = 'delprinc -force'

    cmd = __execute_kadmin(krb_cmd + ' {0}'.format(name))

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    return True