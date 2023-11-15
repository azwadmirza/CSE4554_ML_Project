def execute(context=None, lens=None, commands=(), load_path=None):
    '''
    Execute Augeas commands

    .. versionadded:: 2014.7.0

    CLI Example:

    .. code-block:: bash

        salt '*' augeas.execute /files/etc/redis/redis.conf \\
        commands='["set bind 0.0.0.0", "set maxmemory 1G"]'

    context
        The Augeas context

    lens
        The Augeas lens to use

    commands
        The Augeas commands to execute

    .. versionadded:: 2016.3.0

    load_path
        A colon-spearated list of directories that modules should be searched
        in. This is in addition to the standard load path and the directories
        in AUGEAS_LENS_LIB.
    '''
    ret = {'retval': False}

    arg_map = {
        'set':    (1, 2),
        'setm':   (2, 3),
        'move':   (2,),
        'insert': (3,),
        'remove': (1,),
    }

    def make_path(path):
        '''
        Return correct path
        '''
        if not context:
            return path

        if path.lstrip('/'):
            if path.startswith(context):
                return path

            path = path.lstrip('/')
            return os.path.join(context, path)
        else:
            return context

    load_path = _check_load_paths(load_path)

    flags = _Augeas.NO_MODL_AUTOLOAD if lens and context else _Augeas.NONE
    aug = _Augeas(flags=flags, loadpath=load_path)

    if lens and context:
        aug.add_transform(lens, re.sub('^/files', '', context))
        aug.load()

    for command in commands:
        try:
            # first part up to space is always the
            # command name (i.e.: set, move)
            cmd, arg = command.split(' ', 1)

            if cmd not in METHOD_MAP:
                ret['error'] = 'Command {0} is not supported (yet)'.format(cmd)
                return ret

            method = METHOD_MAP[cmd]
            nargs = arg_map[method]

            parts = salt.utils.args.shlex_split(arg)

            if len(parts) not in nargs:
                err = '{0} takes {1} args: {2}'.format(method, nargs, parts)
                raise ValueError(err)
            if method == 'set':
                path = make_path(parts[0])
                value = parts[1] if len(parts) == 2 else None
                args = {'path': path, 'value': value}
            elif method == 'setm':
                base = make_path(parts[0])
                sub = parts[1]
                value = parts[2] if len(parts) == 3 else None
                args = {'base': base, 'sub': sub, 'value': value}
            elif method == 'move':
                path = make_path(parts[0])
                dst = parts[1]
                args = {'src': path, 'dst': dst}
            elif method == 'insert':
                label, where, path = parts
                if where not in ('before', 'after'):
                    raise ValueError(
                        'Expected "before" or "after", not {0}'.format(where))
                path = make_path(path)
                args = {
                    'path': path,
                    'label': label,
                    'before': where == 'before'}
            elif method == 'remove':
                path = make_path(parts[0])
                args = {'path': path}
        except ValueError as err:
            log.error(err)
            # if command.split fails arg will not be set
            if 'arg' not in locals():
                arg = command
            ret['error'] = 'Invalid formatted command, ' \
                           'see debug log for details: {0}'.format(arg)
            return ret

        log.debug('%s: %s', method, args)

        func = getattr(aug, method)
        func(**args)

    try:
        aug.save()
        ret['retval'] = True
    except IOError as err:
        ret['error'] = six.text_type(err)

        if lens and not lens.endswith('.lns'):
            ret['error'] += '\nLenses are normally configured as "name.lns". ' \
                            'Did you mean "{0}.lns"?'.format(lens)

    aug.close()
    return ret