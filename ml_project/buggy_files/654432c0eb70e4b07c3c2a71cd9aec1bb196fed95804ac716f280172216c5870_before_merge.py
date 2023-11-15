def search(filter,      # pylint: disable=C0103
           dn=None,     # pylint: disable=C0103
           scope=None,
           attrs=None,
           **kwargs):
    '''
    Run an arbitrary LDAP query and return the results.

    CLI Example:

    .. code-block:: bash

        salt 'ldaphost' ldap.search "filter=cn=myhost"

    Return data:

    .. code-block:: python

        {'myhost': {'count': 1,
                    'results': [['cn=myhost,ou=hosts,o=acme,c=gb',
                                 {'saltKeyValue': ['ntpserver=ntp.acme.local',
                                                   'foo=myfoo'],
                                  'saltState': ['foo', 'bar']}]],
                    'time': {'human': '1.2ms', 'raw': '0.00123'}}}

    Search and connection options can be overridden by specifying the relevant
    option as key=value pairs, for example:

    .. code-block:: bash

        salt 'ldaphost' ldap.search filter=cn=myhost dn=ou=hosts,o=acme,c=gb
        scope=1 attrs='' server='localhost' port='7393' tls=True bindpw='ssh'
    '''
    if not dn:
        dn = _config('dn', 'basedn')  # pylint: disable=C0103
    if not scope:
        scope = _config('scope')
    if attrs == '':  # Allow command line 'return all' attr override
        attrs = None
    elif attrs is None:
        attrs = _config('attrs')
    _ldap = _connect(**kwargs)
    start = time.time()
    log.debug(
        'Running LDAP search with filter:%s, dn:%s, scope:%s, '
        'attrs:%s', filter, dn, scope, attrs
    )
    results = _ldap.search_s(dn, int(scope), filter, attrs)
    elapsed = (time.time() - start)
    if elapsed < 0.200:
        elapsed_h = six.text_type(round(elapsed * 1000, 1)) + 'ms'
    else:
        elapsed_h = six.text_type(round(elapsed, 2)) + 's'

    ret = {
        'results': results,
        'count': len(results),
        'time': {'human': elapsed_h, 'raw': six.text_type(round(elapsed, 5))},
    }
    return ret