def filter_by(lookup_dict, grain='os_family', merge=None, default='default', base=None):
    '''
    .. versionadded:: 0.17.0

    Look up the given grain in a given dictionary for the current OS and return
    the result

    Although this may occasionally be useful at the CLI, the primary intent of
    this function is for use in Jinja to make short work of creating lookup
    tables for OS-specific data. For example:

    .. code-block:: jinja

        {% set apache = salt['grains.filter_by']({
            'Debian': {'pkg': 'apache2', 'srv': 'apache2'},
            'RedHat': {'pkg': 'httpd', 'srv': 'httpd'},
        }, default='Debian') %}

        myapache:
          pkg.installed:
            - name: {{ apache.pkg }}
          service.running:
            - name: {{ apache.srv }}

    Values in the lookup table may be overridden by values in Pillar. An
    example Pillar to override values in the example above could be as follows:

    .. code-block:: yaml

        apache:
          lookup:
            pkg: apache_13
            srv: apache

    The call to ``filter_by()`` would be modified as follows to reference those
    Pillar values:

    .. code-block:: jinja

        {% set apache = salt['grains.filter_by']({
            ...
        }, merge=salt['pillar.get']('apache:lookup')) %}


    :param lookup_dict: A dictionary, keyed by a grain, containing a value or
        values relevant to systems matching that grain. For example, a key
        could be the grain for an OS and the value could the name of a package
        on that particular OS.

        .. versionchanged:: 2016.11.0

            The dictionary key could be a globbing pattern. The function will
            return the corresponding ``lookup_dict`` value where grain value
            matches the pattern. For example:

            .. code-block:: bash

                # this will render 'got some salt' if Minion ID begins from 'salt'
                salt '*' grains.filter_by '{salt*: got some salt, default: salt is not here}' id

    :param grain: The name of a grain to match with the current system's
        grains. For example, the value of the "os_family" grain for the current
        system could be used to pull values from the ``lookup_dict``
        dictionary.

        .. versionchanged:: 2016.11.0

            The grain value could be a list. The function will return the
            ``lookup_dict`` value for a first found item in the list matching
            one of the ``lookup_dict`` keys.

    :param merge: A dictionary to merge with the results of the grain selection
        from ``lookup_dict``. This allows Pillar to override the values in the
        ``lookup_dict``. This could be useful, for example, to override the
        values for non-standard package names such as when using a different
        Python version from the default Python version provided by the OS
        (e.g., ``python26-mysql`` instead of ``python-mysql``).

    :param default: default lookup_dict's key used if the grain does not exists
        or if the grain value has no match on lookup_dict.  If unspecified
        the value is "default".

        .. versionadded:: 2014.1.0

    :param base: A lookup_dict key to use for a base dictionary.  The
        grain-selected ``lookup_dict`` is merged over this and then finally
        the ``merge`` dictionary is merged.  This allows common values for
        each case to be collected in the base and overridden by the grain
        selection dictionary and the merge dictionary.  Default is unset.

        .. versionadded:: 2015.5.0

    CLI Example:

    .. code-block:: bash

        salt '*' grains.filter_by '{Debian: Debheads rule, RedHat: I love my hat}'
        # this one will render {D: {E: I, G: H}, J: K}
        salt '*' grains.filter_by '{A: B, C: {D: {E: F, G: H}}}' 'xxx' '{D: {E: I}, J: K}' 'C'
        # next one renders {A: {B: G}, D: J}
        salt '*' grains.filter_by '{default: {A: {B: C}, D: E}, F: {A: {B: G}}, H: {D: I}}' 'xxx' '{D: J}' 'F' 'default'
        # next same as above when default='H' instead of 'F' renders {A: {B: C}, D: J}
    '''

    ret = None
    # Default value would be an empty list if grain not found
    val = salt.utils.traverse_dict_and_list(__grains__, grain, [])

    # Iterate over the list of grain values to match against patterns in the lookup_dict keys
    for each in val if isinstance(val, list) else [val]:
        for key in sorted(lookup_dict):
            if key not in six.string_types:
                key = str(key)
            if fnmatch.fnmatchcase(each, key):
                ret = lookup_dict[key]
                break
        if ret is not None:
            break

    if ret is None:
        ret = lookup_dict.get(default, None)

    if base and base in lookup_dict:
        base_values = lookup_dict[base]
        if ret is None:
            ret = base_values

        elif isinstance(base_values, collections.Mapping):
            if not isinstance(ret, collections.Mapping):
                raise SaltException(
                    'filter_by default and look-up values must both be dictionaries.')
            ret = salt.utils.dictupdate.update(copy.deepcopy(base_values), ret)

    if merge:
        if not isinstance(merge, collections.Mapping):
            raise SaltException('filter_by merge argument must be a dictionary.')

        if ret is None:
            ret = merge
        else:
            salt.utils.dictupdate.update(ret, copy.deepcopy(merge))

    return ret