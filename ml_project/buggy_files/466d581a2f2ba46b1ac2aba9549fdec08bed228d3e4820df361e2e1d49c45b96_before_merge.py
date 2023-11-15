def get_option(file_name, section, option, separator='='):
    '''
    Get value of a key from a section in an ini file. Returns ``None`` if
    no matching key was found.

    API Example:

    .. code-block:: python

        import salt
        sc = salt.client.get_local_client()
        sc.cmd('target', 'ini.get_option',
               [path_to_ini_file, section_name, option])

    CLI Example:

    .. code-block:: bash

        salt '*' ini.get_option /path/to/ini section_name option_name
    '''
    inifile = _Ini.get_ini_file(file_name, separator=separator)
    return inifile.get(section, {}).get(option, None)