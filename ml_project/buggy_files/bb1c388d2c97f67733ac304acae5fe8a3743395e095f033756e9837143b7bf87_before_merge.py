def run(
    name,
    onlyif=None,
    unless=None,
    creates=None,
    cwd=None,
    root=None,
    runas=None,
    shell=None,
    env=None,
    prepend_path=None,
    stateful=False,
    umask=None,
    output_loglevel="debug",
    hide_output=False,
    timeout=None,
    ignore_timeout=False,
    use_vt=False,
    success_retcodes=None,
    **kwargs
):
    """
    Run a command if certain circumstances are met.  Use ``cmd.wait`` if you
    want to use the ``watch`` requisite.

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    onlyif
        A command to run as a check, run the named command only if the command
        passed to the ``onlyif`` option returns a zero exit status

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns a non-zero exit status

    cwd
        The current working directory to execute the command in, defaults to
        /root

    root
        Path to the root of the jail to use. If this parameter is set, the command
        will run inside a chroot

    runas
        The user name to run the command as

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
            idiosyncrasies can be found :ref:`here <yaml-idiosyncrasies>`.

        Variables as values are not evaluated. So $PATH in the following
        example is a literal '$PATH':

        .. code-block:: yaml

            script-bar:
              cmd.run:
                - env: "PATH=/some/path:$PATH"

        One can still use the existing $PATH by using a bit of Jinja:

        .. code-block:: jinja

            {% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}

            mycommand:
              cmd.run:
                - name: ls -l /
                - env:
                  - PATH: {{ [current_path, '/my/special/bin']|join(':') }}

    prepend_path
        $PATH segment to prepend (trailing ':' not necessary) to $PATH. This is
        an easier alternative to the Jinja workaround.

        .. versionadded:: 2018.3.0

    stateful
        The command being executed is expected to return data about executing
        a state. For more information, see the :ref:`stateful-argument` section.

    umask
        The umask (in octal) to use when running the command.

    output_loglevel : debug
        Control the loglevel at which the output from the command is logged to
        the minion log.

        .. note::
            The command being run will still be logged at the ``debug``
            loglevel regardless, unless ``quiet`` is used for this value.

    hide_output : False
        Suppress stdout and stderr in the state's results.

        .. note::
            This is separate from ``output_loglevel``, which only handles how
            Salt logs to the minion log.

        .. versionadded:: 2018.3.0

    timeout
        If the command has not terminated after timeout seconds, send the
        subprocess sigterm, and if sigterm is ignored, follow up with sigkill

    ignore_timeout
        Ignore the timeout of commands, which is useful for running nohup
        processes.

        .. versionadded:: 2015.8.0

    creates
        Only run if the file specified by ``creates`` do not exist. If you
        specify a list of files then this state will only run if **any** of
        the files do not exist.

        .. versionadded:: 2014.7.0

    use_vt : False
        Use VT utils (saltstack) to stream the command output more
        interactively to the console and the logs.
        This is experimental.

    bg : False
        If ``True``, run command in background and do not await or deliver its
        results.

        .. versionadded:: 2016.3.6

    success_retcodes: This parameter will be allow a list of
        non-zero return codes that should be considered a success.  If the
        return code returned from the run matches any in the provided list,
        the return code will be overridden with zero.

      .. versionadded:: 2019.2.0

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

    """
    ### NOTE: The keyword arguments in **kwargs are passed directly to the
    ###       ``cmd.run_all`` function and cannot be removed from the function
    ###       definition, otherwise the use of unsupported arguments in a
    ###       ``cmd.run`` state will result in a traceback.

    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    test_name = None
    if not isinstance(stateful, list):
        stateful = stateful is True
    elif isinstance(stateful, list) and "test_name" in stateful[0]:
        test_name = stateful[0]["test_name"]
    if __opts__["test"] and test_name:
        name = test_name

    # Need the check for None here, if env is not provided then it falls back
    # to None and it is assumed that the environment is not being overridden.
    if env is not None and not isinstance(env, (list, dict)):
        ret["comment"] = "Invalidly-formatted 'env' parameter. See " "documentation."
        return ret

    cmd_kwargs = copy.deepcopy(kwargs)
    cmd_kwargs.update(
        {
            "cwd": cwd,
            "root": root,
            "runas": runas,
            "use_vt": use_vt,
            "shell": shell or __grains__["shell"],
            "env": env,
            "prepend_path": prepend_path,
            "umask": umask,
            "output_loglevel": output_loglevel,
            "hide_output": hide_output,
            "success_retcodes": success_retcodes,
        }
    )

    cret = mod_run_check(cmd_kwargs, onlyif, unless, creates)
    if isinstance(cret, dict):
        ret.update(cret)
        return ret

    if __opts__["test"] and not test_name:
        ret["result"] = None
        ret["comment"] = 'Command "{0}" would have been executed'.format(name)
        return _reinterpreted_state(ret) if stateful else ret

    if cwd and not os.path.isdir(cwd):
        ret["comment"] = ('Desired working directory "{0}" ' "is not available").format(
            cwd
        )
        return ret

    # Wow, we passed the test, run this sucker!
    try:
        run_cmd = "cmd.run_all" if not root else "cmd.run_chroot"
        cmd_all = __salt__[run_cmd](
            cmd=name, timeout=timeout, python_shell=True, **cmd_kwargs
        )
    except Exception as err:  # pylint: disable=broad-except
        ret["comment"] = six.text_type(err)
        return ret

    ret["changes"] = cmd_all
    ret["result"] = not bool(cmd_all["retcode"])
    ret["comment"] = 'Command "{0}" run'.format(name)

    # Ignore timeout errors if asked (for nohups) and treat cmd as a success
    if ignore_timeout:
        trigger = "Timed out after"
        if ret["changes"].get("retcode") == 1 and trigger in ret["changes"].get(
            "stdout"
        ):
            ret["changes"]["retcode"] = 0
            ret["result"] = True

    if stateful:
        ret = _reinterpreted_state(ret)
    if __opts__["test"] and cmd_all["retcode"] == 0 and ret["changes"]:
        ret["result"] = None
    return ret