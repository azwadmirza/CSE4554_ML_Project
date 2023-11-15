def modify(connect_spec, dn, directives):
    '''Modify an entry in an LDAP database.

    :param connect_spec:
        See the documentation for the ``connect_spec`` parameter for
        :py:func:`connect`.

    :param dn:
        Distinguished name of the entry.

    :param directives:
        Iterable of directives that indicate how to modify the entry.
        Each directive is a tuple of the form ``(op, attr, vals)``,
        where:

        * ``op`` identifies the modification operation to perform.
          One of:

          * ``'add'`` to add one or more values to the attribute

          * ``'delete'`` to delete some or all of the values from the
            attribute.  If no values are specified with this
            operation, all of the attribute's values are deleted.
            Otherwise, only the named values are deleted.

          * ``'replace'`` to replace all of the attribute's values
            with zero or more new values

        * ``attr`` names the attribute to modify

        * ``vals`` is an iterable of values to add or delete

    :returns:
        ``True`` if successful, raises an exception otherwise.

    CLI example:

    .. code-block:: bash

        salt '*' ldap3.modify "{
            'url': 'ldaps://ldap.example.com/',
            'bind': {
                'method': 'simple',
                'password': 'secret'}
        }" dn='cn=admin,dc=example,dc=com'
        directives="('add', 'example', ['example_val'])"
    '''
    l = connect(connect_spec)
    # convert the "iterable of values" to lists in case that's what
    # modify_s() expects (also to ensure that the caller's objects are
    # not modified)
    modlist = [(getattr(ldap, 'MOD_' + op.upper()), attr, list(vals))
               for op, attr, vals in directives]

    for idx, mod in enumerate(modlist):
        if mod[1] == 'unicodePwd':
            modlist[idx] = (mod[0], mod[1],
                [_format_unicode_password(x) for x in mod[2]])

    modlist = salt.utils.data.decode(modlist, to_str=True)
    try:
        l.c.modify_s(dn, modlist)
    except ldap.LDAPError as e:
        _convert_exception(e)
    return True