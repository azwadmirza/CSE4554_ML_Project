def info(name):
    '''
    Return information for the specified user

    CLI Example:

    .. code-block:: bash

        salt '*' shadow.info someuser
    '''
    try:
        data = pwd.getpwnam(name)
        ret = {
            'name': data.pw_name,
            'passwd': data.pw_passwd}
    except KeyError:
        return {
            'name': '',
            'passwd': ''}

    if not isinstance(name, six.string_types):
        name = six.text_type(name)
    if ':' in name:
        raise SaltInvocationError('Invalid username \'{0}\''.format(name))

    if __salt__['cmd.has_exec']('pw'):
        change, expire = __salt__['cmd.run_stdout'](
            ['pw', 'user', 'show', name],
            python_shell=False).split(':')[5:7]
    elif __grains__['kernel'] in ('NetBSD', 'OpenBSD'):
        try:
            with salt.utils.files.fopen('/etc/master.passwd', 'r') as fp_:
                for line in fp_:
                    line = salt.utils.stringutils.to_unicode(line)
                    if line.startswith('{0}:'.format(name)):
                        key = line.split(':')
                        change, expire = key[5:7]
                        ret['passwd'] = six.text_type(key[1])
                        break
        except IOError:
            change = expire = None
    else:
        change = expire = None

    try:
        ret['change'] = int(change)
    except ValueError:
        pass

    try:
        ret['expire'] = int(expire)
    except ValueError:
        pass

    return ret