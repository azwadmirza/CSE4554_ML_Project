def script(source,
           args=None,
           cwd=None,
           stdin=None,
           runas=None,
           shell=DEFAULT_SHELL,
           env=(),
           template='jinja',
           umask=None,
           timeout=None,
           reset_system_locale=True,
           __env__='base',
           **kwargs):
    '''
    Download a script from a remote location and execute the script locally.
    The script can be located on the salt master file server or on an HTTP/FTP
    server.

    The script will be executed directly, so it can be written in any available
    programming language.

    The script can also be formated as a template, the default is jinja.
    Arguments for the script can be specified as well.

    CLI Example:

    .. code-block:: bash

        salt '*' cmd.script salt://scripts/runme.sh
        salt '*' cmd.script salt://scripts/runme.sh 'arg1 arg2 "arg 3"'
        salt '*' cmd.script salt://scripts/windows_task.ps1 args=' -Input c:\\tmp\\infile.txt' shell='powershell'

    A string of standard input can be specified for the command to be run using
    the ``stdin`` parameter. This can be useful in cases where sensitive
    information must be read from standard input.:

    .. code-block:: bash

        salt '*' cmd.script salt://scripts/runme.sh stdin='one\\ntwo\\nthree\\nfour\\nfive\\n'
    '''

    if isinstance(env, string_types):
        salt.utils.warn_until(
            'Helium',
            'Passing a salt environment should be done using \'__env__\' not '
            '\'env\'. This functionality will be removed in Salt {version}.'
        )
        # Backwards compatibility
        __env__ = env

    if not salt.utils.is_windows():
        path = salt.utils.mkstemp(dir=cwd)
    else:
        path = __salt__['cp.cache_file'](source, __env__)
        if not path:
            return {'pid': 0,
                    'retcode': 1,
                    'stdout': '',
                    'stderr': '',
                    'cache_error': True}
    if template:
        __salt__['cp.get_template'](source, path, template, __env__, **kwargs)
    else:
        if not salt.utils.is_windows():
            fn_ = __salt__['cp.cache_file'](source, __env__)
            if not fn_:
                return {'pid': 0,
                        'retcode': 1,
                        'stdout': '',
                        'stderr': '',
                        'cache_error': True}
            shutil.copyfile(fn_, path)
    if not salt.utils.is_windows():
        os.chmod(path, 320)
        os.chown(path, __salt__['file.user_to_uid'](runas), -1)
    ret = _run(path + ' ' + str(args) if args else path,
               cwd=cwd,
               stdin=stdin,
               quiet=kwargs.get('quiet', False),
               runas=runas,
               shell=shell,
               umask=umask,
               timeout=timeout,
               reset_system_locale=reset_system_locale)
    os.remove(path)
    return ret