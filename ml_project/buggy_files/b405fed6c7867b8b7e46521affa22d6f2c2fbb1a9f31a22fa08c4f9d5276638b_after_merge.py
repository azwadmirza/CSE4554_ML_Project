def create_keytab(name, keytab, enctypes=None):
    '''
    Create keytab

    CLI Example:

    .. code-block:: bash

        salt 'kdc.example.com' kerberos.create_keytab host/host1.example.com host1.example.com.keytab
    '''
    ret = {}

    krb_flavor = __opts__.get('krb_flavor', None)
    if krb_flavor == "heimdal":
        krb_cmd = 'ext_keytab -k {0}'.format(keytab)
    else:
        krb_cmd = 'ktadd -k {0}'.format(keytab)
        if enctypes:
            krb_cmd += ' -e {0}'.format(enctypes)

    krb_cmd += ' {0}'.format(name)

    cmd = __execute_kadmin(krb_cmd)

    if cmd['retcode'] != 0 or cmd['stderr']:
        ret['comment'] = cmd['stderr'].splitlines()[-1]
        ret['result'] = False

        return ret

    return True