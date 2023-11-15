def get_computer_desc():
    '''
    Get PRETTY_HOSTNAME value stored in /etc/machine-info
    If this file doesn't exist or the variable doesn't exist
    return False.

    :return: Value of PRETTY_HOSTNAME if this does not exist False.
    :rtype: str

    CLI Example:

    .. code-block:: bash

        salt '*' system.get_computer_desc
    '''
    hostname_cmd = salt.utils.path.which('hostnamectl')
    if hostname_cmd:
        desc = __salt__['cmd.run'](
            [hostname_cmd, 'status', '--pretty'],
            python_shell=False
        )
    else:
        desc = None
        pattern = re.compile(r'^\s*PRETTY_HOSTNAME=(.*)$')
        try:
            with salt.utils.files.fopen('/etc/machine-info', 'r') as mach_info:
                for line in mach_info.readlines():
                    line = salt.utils.stringutils.to_unicode(line)
                    match = pattern.match(line)
                    if match:
                        # get rid of whitespace then strip off quotes
                        desc = _strip_quotes(match.group(1).strip())
                        # no break so we get the last occurance
        except IOError:
            pass

        if desc is None:
            return False

    return desc.replace(r'\"', r'"').replace(r'\n', '\n').replace(r'\t', '\t')