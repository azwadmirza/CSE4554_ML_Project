def execute(context=None, lens=None, commands=()):
    '''
    Execute Augeas commands

    .. versionadded:: 2014.7.0

    CLI Example:

    .. code-block:: bash

        salt '*' augeas.execute /files/etc/redis/redis.conf commands='["set bind 0.0.0.0", "set maxmemory 1G"]'
    '''
    ret = {'retval': False}

    method_map = {
        'set':    'set',
        'mv':     'move',
        'move':   'move',
        'ins':    'insert',
        'insert': 'insert',
        'rm':     'remove',
        'remove': 'remove',
    }

    flags = _Augeas.NO_MODL_AUTOLOAD if lens else _Augeas.NONE
    aug = _Augeas(flags=flags)

    if lens:
        aug.add_transform(lens, re.sub('^/files', '', context))
        aug.load()

    for command in commands:
        # first part up to space is always the command name (i.e.: set, move)
        cmd, arg = command.split(' ', 1)
        if cmd not in method_map:
            ret['error'] = 'Command {0} is not supported (yet)'.format(cmd)
            return ret

        method = method_map[cmd]

        try:
            if method == 'set':
                path, value, remainder = re.split('([^\'" ]+|"[^"]+"|\'[^\']+\')$', arg, 1)
                if context:
                    path = os.path.join(context.rstrip('/'), path.lstrip('/'))
                value = value.strip('"').strip("'")
                args = {'path': path, 'value': value}
            elif method == 'move':
                path, dst = arg.split(' ', 1)
                if context:
                    path = os.path.join(context.rstrip('/'), path.lstrip('/'))
                args = {'src': path, 'dst': dst}
            elif method == 'insert':
                label, where, path = re.split(' (before|after) ', arg)
                if context:
                    path = os.path.join(context.rstrip('/'), path.lstrip('/'))
                args = {'path': path, 'label': label, 'before': where == 'before'}
            elif method == 'remove':
                path = arg
                if context:
                    path = os.path.join(context.rstrip('/'), path.lstrip('/'))
                args = {'path': path}
        except ValueError as err:
            log.error(str(err))
            ret['error'] = 'Invalid formatted command, ' \
                           'see debug log for details: {0}'.format(arg)
            return ret

        log.debug('{0}: {1}'.format(method, args))

        func = getattr(aug, method)
        func(**args)

    try:
        aug.save()
        ret['retval'] = True
    except IOError as err:
        ret['error'] = str(err)

        if lens and not lens.endswith('.lns'):
            ret['error'] += '\nLenses are normally configured as "name.lns". ' \
                            'Did you mean "{0}.lns"?'.format(lens)

    aug.close()
    return ret