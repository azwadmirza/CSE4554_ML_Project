def change(connect_spec, dn, before, after):
    '''Modify an entry in an LDAP database.

    This does the same thing as :py:func:`modify`, but with a simpler
    interface.  Instead of taking a list of directives, it takes a
    before and after view of an entry, determines the differences
    between the two, computes the directives, and executes them.

    Any attribute value present in ``before`` but missing in ``after``
    is deleted.  Any attribute value present in ``after`` but missing
    in ``before`` is added.  Any attribute value in the database that
    is not mentioned in either ``before`` or ``after`` is not altered.
    Any attribute value that is present in both ``before`` and
    ``after`` is ignored, regardless of whether that attribute value
    exists in the database.

    :param connect_spec:
        See the documentation for the ``connect_spec`` parameter for
        :py:func:`connect`.

    :param dn:
        Distinguished name of the entry.

    :param before:
        The expected state of the entry before modification.  This is
        a dict mapping each attribute name to an iterable of values.

    :param after:
        The desired state of the entry after modification.  This is a
        dict mapping each attribute name to an iterable of values.

    :returns:
        ``True`` if successful, raises an exception otherwise.

    CLI example:

    .. code-block:: bash

        salt '*' ldap3.change "{
            'url': 'ldaps://ldap.example.com/',
            'bind': {
                'method': 'simple',
                'password': 'secret'}
        }" dn='cn=admin,dc=example,dc=com'
        before="{'example_value': 'before_val'}"
        after="{'example_value': 'after_val'}"
    '''
    l = connect(connect_spec)
    # convert the "iterable of values" to lists in case that's what
    # modifyModlist() expects (also to ensure that the caller's dicts
    # are not modified)
    before = dict(((attr, list(vals))
                   for attr, vals in six.iteritems(before)))
    after = dict(((attr, list(vals))
                  for attr, vals in six.iteritems(after)))

    if 'unicodePwd' in after:
        after['unicodePwd'] = [_format_unicode_password(x) for x in after['unicodePwd']]

    modlist = ldap.modlist.modifyModlist(before, after)
    try:
        l.c.modify_s(dn, modlist)
    except ldap.LDAPError as e:
        _convert_exception(e)
    return True