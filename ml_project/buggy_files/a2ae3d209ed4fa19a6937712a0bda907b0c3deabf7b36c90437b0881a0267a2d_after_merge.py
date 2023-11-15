def set_(key, value, setting=None, conf_file=_DEFAULT_CONF):
    '''
    Set a new value for a specific configuration line.

    :param str key: The command or block to configure.
    :param str value: The command value or command of the block specified by the key parameter.
    :param str setting: The command value for the command specified by the value parameter.
    :param str conf_file: The logrotate configuration file.

    :return: A boolean representing whether all changes succeeded.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' logrotate.set rotate 2

    Can also be used to set a single value inside a multiline configuration
    block. For instance, to change rotate in the following block:

    .. code-block:: text

        /var/log/wtmp {
            monthly
            create 0664 root root
            rotate 1
        }

    Use the following command:

    .. code-block:: bash

        salt '*' logrotate.set /var/log/wtmp rotate 2

    This module also has the ability to scan files inside an include directory,
    and make changes in the appropriate file.
    '''
    conf = _parse_conf(conf_file)
    for include in conf.setdefault('include files', {}):
        if key in conf['include files'][include]:
            conf_file = os.path.join(conf['include'], include)

    new_line = six.text_type()
    kwargs = {
        'flags': 8,
        'backup': False,
        'path': conf_file,
        'pattern': '^{0}.*'.format(key),
        'show_changes': False
    }

    if setting is None:
        current_value = conf.get(key, False)

        if isinstance(current_value, dict):
            error_msg = ('Error: {0} includes a dict, and a specific setting inside the '
                         'dict was not declared').format(key)
            raise SaltInvocationError(error_msg)

        if value == current_value:
            _LOG.debug("Command '%s' already has: %s", key, value)
            return True

        # This is the new config line that will be set
        if value is True:
            new_line = key
        elif value:
            new_line = '{0} {1}'.format(key, value)

        kwargs.update({'prepend_if_not_found': True})
    else:
        stanza = conf.get(key, dict())

        if stanza and not isinstance(stanza, dict):
            error_msg = ('Error: A setting for a dict was declared, but the '
                         'configuration line given is not a dict')
            raise SaltInvocationError(error_msg)

        if setting == stanza.get(value, False):
            _LOG.debug("Command '%s' already has: %s", value, setting)
            return True

        # We're going to be rewriting an entire stanza
        if setting:
            stanza[value] = setting
        else:
            del stanza[value]

        new_line = _dict_to_stanza(key, stanza)

        kwargs.update({
            'pattern': '^{0}.*?{{.*?}}'.format(key),
            'flags': 24,
            'append_if_not_found': True
        })

    kwargs.update({'repl': new_line})
    _LOG.debug("Setting file '%s' line: %s", conf_file, new_line)

    return __salt__['file.replace'](**kwargs)