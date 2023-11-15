def remove_option(file_name, section, option, separator='='):
    '''
    Remove a key/value pair from a section in an ini file. Returns the value of
    the removed key, or ``None`` if nothing was removed.

    API Example:

    .. code-block:: python

        import salt
        sc = salt.client.get_local_client()
        sc.cmd('target', 'ini.remove_option',
               [path_to_ini_file, section_name, option])

    CLI Example:

    .. code-block:: bash

        salt '*' ini.remove_option /path/to/ini section_name option_name
    '''
    inifile = _Ini.get_ini_file(file_name, separator=separator)
    if isinstance(inifile.get(section), (dict, OrderedDict)):
        value = inifile.get(section, {}).pop(option, None)
    else:
        value = inifile.pop(option, None)
    inifile.flush()
    return value