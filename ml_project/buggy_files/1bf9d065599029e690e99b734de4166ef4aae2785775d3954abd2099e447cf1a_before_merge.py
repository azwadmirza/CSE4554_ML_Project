def cd(args, stdin=None):
    """Changes the directory.

    If no directory is specified (i.e. if `args` is None) then this
    changes to the current user's home directory.
    """
    env = builtins.__xonsh_env__
    oldpwd = env.get('OLDPWD', None)
    cwd = env['PWD']

    if len(args) == 0:
        d = os.path.expanduser('~')
    elif len(args) == 1:
        d = os.path.expanduser(args[0])
        if not os.path.isdir(d):
            if d == '-':
                if oldpwd is not None:
                    d = oldpwd
                else:
                    return '', 'cd: no previous directory stored\n', 1
            elif d.startswith('-'):
                try:
                    num = int(d[1:])
                except ValueError:
                    return '', 'cd: Invalid destination: {0}\n'.format(d), 1
                if num == 0:
                    return None, None, 0
                elif num < 0:
                    return '', 'cd: Invalid destination: {0}\n'.format(d), 1
                elif num > len(DIRSTACK):
                    e = 'cd: Too few elements in dirstack ({0} elements)\n'
                    return '', e.format(len(DIRSTACK)), 1
                else:
                    d = DIRSTACK[num - 1]
            else:
                d = _try_cdpath(d)
    else:
        return '', 'cd takes 0 or 1 arguments, not {0}\n'.format(len(args)), 1
    if not os.path.exists(d):
        return '', 'cd: no such file or directory: {0}\n'.format(d), 1
    if not os.path.isdir(d):
        return '', 'cd: {0} is not a directory\n'.format(d), 1
    if not os.access(d, os.X_OK):
        return '', 'cd: permission denied: {0}\n'.format(d), 1
    if ON_WINDOWS and (d[0] == d[1]) and (d[0] in (os.sep, os.altsep)) \
            and _unc_check_enabled() and (not env.get('AUTO_PUSHD')):
        return '', "cd: can't cd to UNC path on Windows, unless $AUTO_PUSHD set or reg entry " \
               + r'HKCU\SOFTWARE\MICROSOFT\Command Processor\DisableUNCCheck:DWORD = 1' + '\n', 1

    # now, push the directory onto the dirstack if AUTO_PUSHD is set
    if cwd is not None and env.get('AUTO_PUSHD'):
        pushd(['-n', '-q', cwd])
        if ON_WINDOWS and (d[0] == d[1]) and (d[0] in (os.sep, os.altsep)):
            d = _unc_map_temp_drive(d)
    _change_working_directory(d)
    return None, None, 0