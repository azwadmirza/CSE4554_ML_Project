def get(key, default='', delimiter=DEFAULT_TARGET_DELIM, ordered=True):
    '''
    Attempt to retrieve the named value from grains, if the named value is not
    available return the passed default. The default return is an empty string.

    The value can also represent a value in a nested dict using a ":" delimiter
    for the dict. This means that if a dict in grains looks like this::

        {'pkg': {'apache': 'httpd'}}

    To retrieve the value associated with the apache key in the pkg dict this
    key can be passed::

        pkg:apache

    CLI Example:

    .. code-block:: bash

        salt '*' grains.get pkg:apache
    '''
    if ordered is True:
        grains = __grains__
    else:
        grains = json.loads(json.dumps(__grains__))
    return salt.utils.traverse_dict_and_list(__grains__,
                                             key,
                                             default,
                                             delimiter)