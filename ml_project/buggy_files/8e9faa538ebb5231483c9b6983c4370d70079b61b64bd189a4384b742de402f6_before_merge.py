def script(
    name,
    source=None,
    template=None,
    onlyif=None,
    unless=None,
    creates=None,
    cwd=None,
    runas=None,
    shell=None,
    env=None,
    stateful=False,
    umask=None,
    timeout=None,
    use_vt=False,
    output_loglevel="debug",
    hide_output=False,
    defaults=None,
    context=None,
    success_retcodes=None,
    **kwargs
):
    """
    Download a script and execute it with specified arguments.

    source
        The location of the script to download. If the file is located on the
        master in the directory named spam, and is called eggs, the source
        string is salt://spam/eggs

    template
        If this setting is applied then the named templating engine will be
        used to render the downloaded file. Currently jinja, mako, and wempy
        are supported

    name
        Either "cmd arg1 arg2 arg3..." (cmd is not used) or a source
        "salt://...".

    onlyif
        Run the named command only if the command passed to the ``onlyif``
        option returns true

    unless
        Run the named command only if the command passed to the ``unless``
        option returns false

    cwd
        The current working directory to execute the command in, defaults to
        /root

    runas
        The name of the user to run the command as

    shell
        The shell to use for execution. The default is set in grains['shell']

    env
        A list of environment variables to be set prior to execution.
        Example:

        .. code-block:: yaml

            salt://scripts/foo.sh:
              cmd.script:
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

            salt://scripts/bar.sh:
              cmd.script:
                - env: "PATH=/some/path:$PATH"

        One can still use the existing $PATH by using a bit of Jinja:

        .. code-block:: jinja

            {% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}

            mycommand:
              cmd.run:
                - name: ls -l /
                - env:
                  - PATH: {{ [current_path, '/my/special/bin']|join(':') }}

    saltenv : ``base``
        The Salt environment to use

    umask
         The umask (in octal) to use when running the command.

    stateful
        The command being executed is expected to return data about executing
        a state. For more information, see the :ref:`stateful-argument` section.

    timeout
        If the command has not terminated after timeout seconds, send the
        subprocess sigterm, and if sigterm is ignored, follow up with sigkill

    args
        String of command line args to pass to the script.  Only used if no
        args are specified as part of the `name` argument. To pass a string
        containing spaces in YAML, you will need to doubly-quote it:  "arg1
        'arg two' arg3"

    creates
        Only run if the file specified by ``creates`` do not exist. If you
        specify a list of files then this state will only run if **any** of
        the files do not exist.

        .. versionadded:: 2014.7.0

    use_vt
        Use VT utils (saltstack) to stream the command output more
        interactively to the console and the logs.
        This is experimental.

    context
        .. versionadded:: 2016.3.0

        Overrides default context variables passed to the template.

    defaults
        .. versionadded:: 2016.3.0

        Default context passed to the template.

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

    success_retcodes: This parameter will be allow a list of
        non-zero return codes that should be considered a success.  If the
        return code returned from the run matches any in the provided list,
        the return code will be overridden with zero.

      .. versionadded:: 2019.2.0

    """
    test_name = None
    if not isinstance(stateful, list):
        stateful = stateful is True
    elif isinstance(stateful, list) and "test_name" in stateful[0]:
        test_name = stateful[0]["test_name"]
    if __opts__["test"] and test_name:
        name = test_name

    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    # Need the check for None here, if env is not provided then it falls back
    # to None and it is assumed that the environment is not being overridden.
    if env is not None and not isinstance(env, (list, dict)):
        ret["comment"] = "Invalidly-formatted 'env' parameter. See " "documentation."
        return ret

    if context and not isinstance(context, dict):
        ret["comment"] = (
            "Invalidly-formatted 'context' parameter. Must " "be formed as a dict."
        )
        return ret
    if defaults and not isinstance(defaults, dict):
        ret["comment"] = (
            "Invalidly-formatted 'defaults' parameter. Must " "be formed as a dict."
        )
        return ret

    tmpctx = defaults if defaults else {}
    if context:
        tmpctx.update(context)

    cmd_kwargs = copy.deepcopy(kwargs)
    cmd_kwargs.update(
        {
            "runas": runas,
            "shell": shell or __grains__["shell"],
            "env": env,
            "onlyif": onlyif,
            "unless": unless,
            "cwd": cwd,
            "template": template,
            "umask": umask,
            "timeout": timeout,
            "output_loglevel": output_loglevel,
            "hide_output": hide_output,
            "use_vt": use_vt,
            "context": tmpctx,
            "saltenv": __env__,
            "success_retcodes": success_retcodes,
        }
    )

    run_check_cmd_kwargs = {
        "cwd": cwd,
        "runas": runas,
        "shell": shell or __grains__["shell"],
    }

    # Change the source to be the name arg if it is not specified
    if source is None:
        source = name

    # If script args present split from name and define args
    if not cmd_kwargs.get("args", None) and len(name.split()) > 1:
        cmd_kwargs.update({"args": name.split(" ", 1)[1]})

    cret = mod_run_check(run_check_cmd_kwargs, onlyif, unless, creates)
    if isinstance(cret, dict):
        ret.update(cret)
        return ret

    if __opts__["test"] and not test_name:
        ret["result"] = None
        ret["comment"] = "Command '{0}' would have been " "executed".format(name)
        return _reinterpreted_state(ret) if stateful else ret

    if cwd and not os.path.isdir(cwd):
        ret["comment"] = ('Desired working directory "{0}" ' "is not available").format(
            cwd
        )
        return ret

    # Wow, we passed the test, run this sucker!
    try:
        cmd_all = __salt__["cmd.script"](source, python_shell=True, **cmd_kwargs)
    except (CommandExecutionError, SaltRenderError, IOError) as err:
        ret["comment"] = six.text_type(err)
        return ret

    ret["changes"] = cmd_all
    if kwargs.get("retcode", False):
        ret["result"] = not bool(cmd_all)
    else:
        ret["result"] = not bool(cmd_all["retcode"])
    if ret.get("changes", {}).get("cache_error"):
        ret["comment"] = "Unable to cache script {0} from saltenv " "'{1}'".format(
            source, __env__
        )
    else:
        ret["comment"] = "Command '{0}' run".format(name)
    if stateful:
        ret = _reinterpreted_state(ret)
    if __opts__["test"] and cmd_all["retcode"] == 0 and ret["changes"]:
        ret["result"] = None
    return ret