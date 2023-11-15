def set_computer_desc(desc):
    '''
    Set PRETTY_HOSTNAME value stored in /etc/machine-info
    This will create the file if it does not exist. If
    it is unable to create or modify this file returns False.

    :param str desc: The computer description
    :return: False on failure. True if successful.

    CLI Example:

    .. code-block:: bash

        salt '*' system.set_computer_desc "Michael's laptop"
    '''
    desc = salt.utils.stringutils.to_unicode(
        desc).replace('"', r'\"').replace('\n', r'\n').replace('\t', r'\t')

    hostname_cmd = salt.utils.path.which('hostnamectl')
    if hostname_cmd:
        result = __salt__['cmd.retcode'](
            [hostname_cmd, 'set-hostname', '--pretty', desc],
            python_shell=False
        )
        return True if result == 0 else False

    if not os.path.isfile('/etc/machine-info'):
        with salt.utils.files.fopen('/etc/machine-info', 'w'):
            pass

    pattern = re.compile(r'^\s*PRETTY_HOSTNAME=(.*)$')
    new_line = salt.utils.stringutils.to_str('PRETTY_HOSTNAME="{0}"'.format(desc))
    try:
        with salt.utils.files.fopen('/etc/machine-info', 'r+') as mach_info:
            lines = mach_info.readlines()
            for i, line in enumerate(lines):
                if pattern.match(salt.utils.stringutils.to_unicode(line)):
                    lines[i] = new_line
                    break
            else:
                # PRETTY_HOSTNAME line was not found, add it to the end
                lines.append(new_line)
            # time to write our changes to the file
            mach_info.seek(0, 0)
            mach_info.truncate()
            mach_info.writelines(lines)
            return True
    except IOError:
        return False