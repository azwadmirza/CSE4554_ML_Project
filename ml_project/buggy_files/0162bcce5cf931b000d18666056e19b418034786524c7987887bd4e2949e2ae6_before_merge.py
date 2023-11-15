def __execute_kadmin(cmd):
    '''
    Execute kadmin commands
    '''
    ret = {}

    auth_keytab = __opts__.get('auth_keytab', None)
    auth_principal = __opts__.get('auth_principal', None)

    if __salt__['file.file_exists'](auth_keytab) and auth_principal:
        return __salt__['cmd.run_all'](
            'kadmin -k -t {0} -p {1} -q "{2}"'.format(
                auth_keytab, auth_principal, cmd
            )
        )
    else:
        log.error('Unable to find kerberos keytab/principal')
        ret['retcode'] = 1
        ret['comment'] = 'Missing authentication keytab/principal'

    return ret