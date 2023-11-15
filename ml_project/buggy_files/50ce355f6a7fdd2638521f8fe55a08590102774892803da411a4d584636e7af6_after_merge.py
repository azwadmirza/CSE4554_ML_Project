def get(key, default='', merge=False, delimiter=':'):
    '''
    .. versionadded:: 0.14

    Attempt to retrieve the named value from pillar, if the named value is not
    available return the passed default. The default return is an empty string.

    The value can also represent a value in a nested dict using a ":" delimiter
    for the dict. This means that if a dict in pillar looks like this::

        {'pkg': {'apache': 'httpd'}}

    To retrieve the value associated with the apache key in the pkg dict this
    key can be passed::

        pkg:apache

    merge
        Specify whether or not the retrieved values should be recursively
        merged into the passed default.

        .. versionadded:: 2015.5.1

    delimiter
        Specify an alternate delimiter to use when traversing a nested dict

        .. versionadded:: 2015.5.1

    CLI Example:

    .. code-block:: bash

        salt '*' pillar.get pkg:apache
    '''
    if merge:
        ret = salt.utils.traverse_dict_and_list(__pillar__, key, {}, delimiter)
        if isinstance(ret, collections.Mapping) and \
                isinstance(default, collections.Mapping):
            return salt.utils.dictupdate.update(default, ret)

    return salt.utils.traverse_dict_and_list(__pillar__,
                                             key,
                                             default,
                                             delimiter)