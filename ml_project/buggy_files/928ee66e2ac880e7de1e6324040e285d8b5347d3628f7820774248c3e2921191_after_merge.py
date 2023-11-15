def script(name,
           source=None,
           template=None,
           onlyif=None,
           unless=None,
           cwd=None,
           user=None,
           group=None,
           shell=None,
           env=None,
           stateful=False,
           umask=None,
           timeout=None,
           __env__='base',
           **kwargs):
    '''
    Download a script from a remote source and execute it. The name can be the
    source or the source value can be defined.

    source
        The source script being downloaded to the minion, this source script is
        hosted on the salt master server.  If the file is located on the master
        in the directory named spam, and is called eggs, the source string is
        salt://spam/eggs

    template
        If this setting is applied then the named templating engine will be
        used to render the downloaded file, currently jinja, mako, and wempy
        are supported

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    onlyif
        A command to run as a check, run the named command only if the command
        passed to the ``onlyif`` option returns true

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns false

    cwd
        The current working directory to execute the command in, defaults to
        /root

    user
        The user name to run the command as

    group
        The group context to run the command as

    shell
        The shell to use for execution, defaults to the shell grain

    env
        Pass in a list or dict of environment variables to be applied to the
        command upon execution

    umask
         The umask (in octal) to use when running the command.

    stateful
        The command being executed is expected to return data about executing
        a state

    timeout
        If the command has not terminated after timeout seconds, send the
        subprocess sigterm, and if sigterm is ignored, follow up with sigkill

    args
        String of command line args to pass to the script.  Only used if no
        args are specified as part of the `name` argument.

    __env__
        The root directory of the environment for the referencing script. The
        environments are defined in the master config file.

    '''
    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': False}

    if cwd and not os.path.isdir(cwd):
        ret['comment'] = 'Desired working directory is not available'
        return ret

    if isinstance(env, string_types):
        msg = (
            'Passing a salt environment should be done using \'__env__\' not '
            '\'env\'. This warning will go away in Salt {version} and this '
            'will be the default and expected behaviour. Please update your '
            'state files.'
        )
        salt.utils.warn_until('Helium', msg)
        ret.setdefault('warnings', []).append(msg)
        # Backwards compatibility
        __env__ = env

    if HAS_GRP:
        pgid = os.getegid()

    cmd_kwargs = copy.deepcopy(kwargs)
    cmd_kwargs.update({'runas': user,
                       'shell': shell or __grains__['shell'],
                       'env': env,
                       'onlyif': onlyif,
                       'unless': unless,
                       'user': user,
                       'group': group,
                       'cwd': cwd,
                       'template': template,
                       'umask': umask,
                       'timeout': timeout,
                       '__env__': __env__})

    run_check_cmd_kwargs = {
        'cwd': cwd,
        'runas': user,
        'shell': shell or __grains__['shell']
    }

    # Change the source to be the name arg if it is not specified
    if source is None:
        source = name

    # If script args present split from name and define args
    if len(name.split()) > 1:
        cmd_kwargs.update({'args': name.split(' ', 1)[1]})

    try:
        cret = _run_check(
            run_check_cmd_kwargs, onlyif, unless, group
        )
        if isinstance(cret, dict):
            ret.update(cret)
            return ret

        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Command "{0}" would have been executed'
            ret['comment'] = ret['comment'].format(name)
            return _reinterpreted_state(ret) if stateful else ret

        # Wow, we passed the test, run this sucker!
        try:
            cmd_all = __salt__['cmd.script'](source, **cmd_kwargs)
        except (CommandExecutionError, IOError) as err:
            ret['comment'] = str(err)
            return ret

        ret['changes'] = cmd_all
        if kwargs.get('retcode', False):
            ret['result'] = not bool(cmd_all)
        else:
            ret['result'] = not bool(cmd_all['retcode'])
        if ret.get('changes', {}).get('cache_error'):
            ret['comment'] = 'Unable to cache script {0} from env ' \
                             '\'{1}\''.format(source, env)
        else:
            ret['comment'] = 'Command "{0}" run'.format(name)
        return _reinterpreted_state(ret) if stateful else ret

    finally:
        if HAS_GRP:
            os.setegid(pgid)