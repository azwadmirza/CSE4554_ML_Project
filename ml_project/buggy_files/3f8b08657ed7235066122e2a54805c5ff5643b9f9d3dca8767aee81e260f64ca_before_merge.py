def create_principal(name, enctypes=None):
    '''
    Create Principal

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.create_principal host/example.com
    '''
    ret = {}

    krb_cmd = 'addprinc -randkey'

    if enctypes:
        krb_cmd += ' -e {0}'.format(enctypes)

    krb_cmd += ' {0}'.format(name)

    cmd = __execute_kadmin(krb_cmd)

    if cmd['retcode'] != 0 or cmd['stderr']:
        if not cmd['stderr'].splitlines()[-1].startswith('WARNING:'):
            ret['comment'] = cmd['stderr'].splitlines()[-1]
            ret['result'] = False

            return ret

    return True