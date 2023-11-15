def add(connect_spec, dn, attributes):
    '''Add an entry to an LDAP database.

    :param connect_spec:
        See the documentation for the ``connect_spec`` parameter for
        :py:func:`connect`.

    :param dn:
        Distinguished name of the entry.

    :param attributes:
        Non-empty dict mapping each of the new entry's attributes to a
        non-empty iterable of values.

    :returns:
        ``True`` if successful, raises an exception otherwise.

    CLI example:

    .. code-block:: bash

        salt '*' ldap3.add "{
            'url': 'ldaps://ldap.example.com/',
            'bind': {
                'method': 'simple',
                'password': 'secret',
            },
        }" "dn='dc=example,dc=com'" "attributes={'example': 'values'}"
    '''
    l = connect(connect_spec)
    # convert the "iterable of values" to lists in case that's what
    # addModlist() expects (also to ensure that the caller's objects
    # are not modified)
    attributes = dict(((attr, list(vals))
                       for attr, vals in six.iteritems(attributes)))
    log.info('adding entry: dn: %s attributes: %s', repr(dn), repr(attributes))

    if 'unicodePwd' in attributes:
        attributes['unicodePwd'] = [_format_unicode_password(x) for x in attributes['unicodePwd']]

    modlist = ldap.modlist.addModlist(attributes)
    try:
        l.c.add_s(dn, modlist)
    except ldap.LDAPError as e:
        _convert_exception(e)
    return True