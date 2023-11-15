def remove_section(file_name, section, separator='='):
    '''
    Remove a section in an ini file. Returns the removed section as dictionary,
    or ``None`` if nothing was removed.

    API Example:

    .. code-block:: python

        import salt
        sc = salt.client.get_local_client()
        sc.cmd('target', 'ini.remove_section',
               [path_to_ini_file, section_name])

    CLI Example:

    .. code-block:: bash

        salt '*' ini.remove_section /path/to/ini section_name
    '''
    inifile = _Ini.get_ini_file(file_name, separator=separator)
    if section in inifile:
        section = inifile.pop(section)
        inifile.flush()
        ret = {}
        for key, value in six.iteritems(section):
            if key[0] != '#':
                ret.update({key: value})
        return ret