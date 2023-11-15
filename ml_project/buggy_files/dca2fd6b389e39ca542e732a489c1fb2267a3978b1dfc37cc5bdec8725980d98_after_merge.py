def wait(
    name,
    cwd=None,
    root=None,
    runas=None,
    shell=None,
    env=(),
    stateful=False,
    umask=None,
    output_loglevel="debug",
    hide_output=False,
    use_vt=False,
    success_retcodes=None,
    **kwargs
):
    """
    Run the given command only if the watch statement calls it.

    .. note::

        Use :mod:`cmd.run <salt.states.cmd.run>` together with :mod:`onchanges </ref/states/requisites#onchanges>`
        instead of :mod:`cmd.wait <salt.states.cmd.wait>`.

    name
        The command to execute, remember that the command will execute with the
        path and permissions of the salt-minion.

    cwd
        The current working directory to execute the command in, defaults to
        /root

    root
        Path to the root of the jail to use. If this parameter is set, the command
        will run inside a chroot

    runas
        The user name to run the command as

    shell
        The shell to use for execution, defaults to /bin/sh

    env
        A list of environment variables to be set prior to execution.
        Example:

        .. code-block:: yaml

            script-foo:
              cmd.wait:
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
              cmd.wait:
                - env: "PATH=/some/path:$PATH"

        One can still use the existing $PATH by using a bit of Jinja:

        .. code-block:: jinja

            {% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}

            mycommand:
              cmd.run:
                - name: ls -l /
                - env:
                  - PATH: {{ [current_path, '/my/special/bin']|join(':') }}

    umask
         The umask (in octal) to use when running the command.

    stateful
        The command being executed is expected to return data about executing
        a state. For more information, see the :ref:`stateful-argument` section.

    creates
        Only run if the file specified by ``creates`` do not exist. If you
        specify a list of files then this state will only run if **any** of
        the files do not exist.

        .. versionadded:: 2014.7.0

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

    use_vt
        Use VT utils (saltstack) to stream the command output more
        interactively to the console and the logs.
        This is experimental.

    success_retcodes: This parameter will be allow a list of
        non-zero return codes that should be considered a success.  If the
        return code returned from the run matches any in the provided list,
        the return code will be overridden with zero.

      .. versionadded:: 2019.2.0
    """
    # Ignoring our arguments is intentional.
    return {"name": name, "changes": {}, "result": True, "comment": ""}