def run(name,
        onlyif=None,
        unless=None,
        creates=None,
        cwd=None,
        user=None,
        group=None,
        shell=None,
        env=None,
        stateful=False,
        umask=None,
        output_loglevel='debug',
        quiet=False,
        timeout=None,
        ignore_timeout=False,
        use_vt=False,
        **kwargs):
    '''
    Run a command if certain circumstances are met.  Use ``cmd.wait`` if you
    want to use the ``watch`` requisite.

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
        A list of environment variables to be set prior to execution.
        Example:

        .. code-block:: yaml

            script-foo:
              cmd.run:
                - env:
                  - BATCH: 'yes'

        .. warning::

            The above illustrates a common PyYAML pitfall, that **yes**,
            **no**, **on**, **off**, **true**, and **false** are all loaded as
            boolean ``True`` and ``False`` values, and must be enclosed in
            quotes to be used as strings. More info on this (and other) PyYAML
            idiosyncrasies can be found :doc:`here
            </topics/troubleshooting/yaml_idiosyncrasies>`.

        Variables as values are not evaluated. So $PATH in the following
        example is a literal '$PATH':

        .. code-block:: yaml

            script-bar:
              cmd.run:
                - env: "PATH=/some/path:$PATH"

        One can still use the existing $PATH by using a bit of Jinja:

        .. code-block:: yaml

            {% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}

            mycommand:
              cmd.run:
                - name: ls -l /
                - env:
                  - PATH: {{ [current_path, '/my/special/bin']|join(':') }}

    stateful
        The command being executed is expected to return data about executing
        a state. For more information, see the :ref:`stateful-argument` section.

    umask
        The umask (in octal) to use when running the command.

    output_loglevel
        Control the loglevel at which the output from the command is logged.
        Note that the command being run will still be logged (loglevel: DEBUG)
        regardless, unless ``quiet`` is used for this value.

    quiet
        The command will be executed quietly, meaning no log entries of the
        actual command or its return data. This is deprecated as of the
        **2014.1.0** release, and is being replaced with
        ``output_loglevel: quiet``.

    timeout
        If the command has not terminated after timeout seconds, send the
        subprocess sigterm, and if sigterm is ignored, follow up with sigkill

    ignore_timeout
        Ignore the timeout of commands, which is useful for running nohup
        processes.

        .. versionadded:: 2015.8.0

    creates
        Only run if the file specified by ``creates`` does not exist.

        .. versionadded:: 2014.7.0

    use_vt
        Use VT utils (saltstack) to stream the command output more
        interactively to the console and the logs.
        This is experimental.

    .. note::

        cmd.run supports the usage of ``reload_modules``. This functionality
        allows you to force Salt to reload all modules. You should only use
        ``reload_modules`` if your cmd.run does some sort of installation
        (such as ``pip``), if you do not reload the modules future items in
        your state which rely on the software being installed will fail.

        .. code-block:: yaml

            getpip:
              cmd.run:
                - name: /usr/bin/python /usr/local/sbin/get-pip.py
                - unless: which pip
                - require:
                  - pkg: python
                  - file: /usr/local/sbin/get-pip.py
                - reload_modules: True

    '''
    ### NOTE: The keyword arguments in **kwargs are ignored in this state, but
    ###       cannot be removed from the function definition, otherwise the use
    ###       of unsupported arguments in a cmd.run state will result in a
    ###       traceback.

    test_name = None
    if not isinstance(stateful, list):
        stateful = stateful is True
    elif isinstance(stateful, list) and 'test_name' in stateful[0]:
        test_name = stateful[0]['test_name']
    if __opts__['test'] and test_name:
        name = test_name

    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if cwd and not os.path.isdir(cwd):
        ret['comment'] = (
            'Desired working directory "{0}" '
            'is not available'
        ).format(cwd)
        return ret

    # Need the check for None here, if env is not provided then it falls back
    # to None and it is assumed that the environment is not being overridden.
    if env is not None and not isinstance(env, (list, dict)):
        ret['comment'] = ('Invalidly-formatted \'env\' parameter. See '
                          'documentation.')
        return ret

    if HAS_GRP:
        pgid = os.getegid()

    cmd_kwargs = {'cwd': cwd,
                  'runas': user,
                  'use_vt': use_vt,
                  'shell': shell or __grains__['shell'],
                  'env': env,
                  'umask': umask,
                  'output_loglevel': output_loglevel,
                  'quiet': quiet}

    try:
        cret = mod_run_check(cmd_kwargs, onlyif, unless, group, creates)
        if isinstance(cret, dict):
            ret.update(cret)
            return ret

        if __opts__['test'] and not test_name:
            ret['result'] = None
            ret['comment'] = 'Command "{0}" would have been executed'.format(name)
            return _reinterpreted_state(ret) if stateful else ret

        # Wow, we passed the test, run this sucker!
        try:
            cmd_all = __salt__['cmd.run_all'](
                name, timeout=timeout, python_shell=True, **cmd_kwargs
            )
        except CommandExecutionError as err:
            ret['comment'] = str(err)
            return ret

        ret['changes'] = cmd_all
        ret['result'] = not bool(cmd_all['retcode'])
        ret['comment'] = 'Command "{0}" run'.format(name)

        # Ignore timeout errors if asked (for nohups) and treat cmd as a success
        if ignore_timeout:
            trigger = 'Timed out after'
            if ret['changes'].get('retcode') == 1 and trigger in ret['changes'].get('stdout'):
                ret['changes']['retcode'] = 0
                ret['result'] = True

        if stateful:
            ret = _reinterpreted_state(ret)
        if __opts__['test'] and cmd_all['retcode'] == 0 and ret['changes']:
            ret['result'] = None
        return ret

    finally:
        if HAS_GRP:
            os.setegid(pgid)