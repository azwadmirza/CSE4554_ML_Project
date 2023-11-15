def powershell(cmd,
        cwd=None,
        stdin=None,
        runas=None,
        shell=DEFAULT_SHELL,
        env=None,
        clean_env=False,
        template=None,
        rstrip=True,
        umask=None,
        output_encoding=None,
        output_loglevel='debug',
        hide_output=False,
        timeout=None,
        reset_system_locale=True,
        ignore_retcode=False,
        saltenv='base',
        use_vt=False,
        password=None,
        depth=None,
        encode_cmd=False,
        **kwargs):
    '''
    Execute the passed PowerShell command and return the output as a dictionary.

    Other ``cmd.*`` functions (besides ``cmd.powershell_all``)
    return the raw text output of the command. This
    function appends ``| ConvertTo-JSON`` to the command and then parses the
    JSON into a Python dictionary. If you want the raw textual result of your
    PowerShell command you should use ``cmd.run`` with the ``shell=powershell``
    option.

    For example:

    .. code-block:: bash

        salt '*' cmd.run '$PSVersionTable.CLRVersion' shell=powershell
        salt '*' cmd.run 'Get-NetTCPConnection' shell=powershell

    .. versionadded:: 2016.3.0

    .. warning::

        This passes the cmd argument directly to PowerShell
        without any further processing! Be absolutely sure that you
        have properly sanitized the command passed to this function
        and do not use untrusted inputs.

    In addition to the normal ``cmd.run`` parameters, this command offers the
    ``depth`` parameter to change the Windows default depth for the
    ``ConvertTo-JSON`` powershell command. The Windows default is 2. If you need
    more depth, set that here.

    .. note::
        For some commands, setting the depth to a value greater than 4 greatly
        increases the time it takes for the command to return and in many cases
        returns useless data.

    :param str cmd: The powershell command to run.

    :param str cwd: The directory from which to execute the command. Defaults
        to the home directory of the user specified by ``runas`` (or the user
        under which Salt is running if ``runas`` is not specified).

    :param str stdin: A string of standard input can be specified for the
      command to be run using the ``stdin`` parameter. This can be useful in cases
      where sensitive information must be read from standard input.

    :param str runas: Specify an alternate user to run the command. The default
        behavior is to run as the user under which Salt is running. If running
        on a Windows minion you must also use the ``password`` argument, and
        the target user account must be in the Administrators group.

    :param str password: Windows only. Required when specifying ``runas``. This
      parameter will be ignored on non-Windows platforms.

      .. versionadded:: 2016.3.0

    :param str shell: Specify an alternate shell. Defaults to the system's
        default shell.

    :param bool python_shell: If False, let python handle the positional
      arguments. Set to True to use shell features, such as pipes or
      redirection.

    :param dict env: Environment variables to be set prior to execution.

        .. note::
            When passing environment variables on the CLI, they should be
            passed as the string representation of a dictionary.

            .. code-block:: bash

                salt myminion cmd.powershell 'some command' env='{"FOO": "bar"}'

    :param bool clean_env: Attempt to clean out all other shell environment
        variables and set only those provided in the 'env' argument to this
        function.

    :param str template: If this setting is applied then the named templating
        engine will be used to render the downloaded file. Currently jinja,
        mako, and wempy are supported.

    :param bool rstrip: Strip all whitespace off the end of output before it is
        returned.

    :param str umask: The umask (in octal) to use when running the command.

    :param str output_encoding: Control the encoding used to decode the
        command's output.

        .. note::
            This should not need to be used in most cases. By default, Salt
            will try to use the encoding detected from the system locale, and
            will fall back to UTF-8 if this fails. This should only need to be
            used in cases where the output of the command is encoded in
            something other than the system locale or UTF-8.

            To see the encoding Salt has detected from the system locale, check
            the `locale` line in the output of :py:func:`test.versions_report
            <salt.modules.test.versions_report>`.

        .. versionadded:: 2018.3.0

    :param str output_loglevel: Control the loglevel at which the output from
        the command is logged to the minion log.

        .. note::
            The command being run will still be logged at the ``debug``
            loglevel regardless, unless ``quiet`` is used for this value.

    :param bool ignore_retcode: If the exit code of the command is nonzero,
        this is treated as an error condition, and the output from the command
        will be logged to the minion log. However, there are some cases where
        programs use the return code for signaling and a nonzero exit code
        doesn't necessarily mean failure. Pass this argument as ``True`` to
        skip logging the output if the command has a nonzero exit code.

    :param bool hide_output: If ``True``, suppress stdout and stderr in the
        return data.

        .. note::
            This is separate from ``output_loglevel``, which only handles how
            Salt logs to the minion log.

        .. versionadded:: 2018.3.0

    :param int timeout: A timeout in seconds for the executed process to return.

    :param bool use_vt: Use VT utils (saltstack) to stream the command output
        more interactively to the console and the logs. This is experimental.

    :param bool reset_system_locale: Resets the system locale

    :param str saltenv: The salt environment to use. Default is 'base'

    :param int depth: The number of levels of contained objects to be included.
        Default is 2. Values greater than 4 seem to greatly increase the time
        it takes for the command to complete for some commands. eg: ``dir``

        .. versionadded:: 2016.3.4

    :param bool encode_cmd: Encode the command before executing. Use in cases
        where characters may be dropped or incorrectly converted when executed.
        Default is False.

    :returns:
        :dict: A dictionary of data returned by the powershell command.

    CLI Example:

    .. code-block:: powershell

        salt '*' cmd.powershell "$PSVersionTable.CLRVersion"
    '''
    if 'python_shell' in kwargs:
        python_shell = kwargs.pop('python_shell')
    else:
        python_shell = True

    # Append PowerShell Object formatting
    # ConvertTo-JSON is only available on Versions of Windows greater than
    # `7.1.7600`. We have to use `platform.version` instead of `__grains__` here
    # because this function is called by `salt/grains/core.py` before
    # `__grains__` is populated
    if salt.utils.versions.version_cmp(platform.version(), '7.1.7600') == 1:
        cmd += ' | ConvertTo-JSON'
        if depth is not None:
            cmd += ' -Depth {0}'.format(depth)

    if encode_cmd:
        # Convert the cmd to UTF-16LE without a BOM and base64 encode.
        # Just base64 encoding UTF-8 or including a BOM is not valid.
        log.debug('Encoding PowerShell command \'%s\'', cmd)
        cmd_utf16 = cmd.decode('utf-8').encode('utf-16le')
        cmd = base64.standard_b64encode(cmd_utf16)
        encoded_cmd = True
    else:
        encoded_cmd = False

    # Put the whole command inside a try / catch block
    # Some errors in PowerShell are not "Terminating Errors" and will not be
    # caught in a try/catch block. For example, the `Get-WmiObject` command will
    # often return a "Non Terminating Error". To fix this, make sure
    # `-ErrorAction Stop` is set in the powershell command
    cmd = 'try {' + cmd + '} catch { "{}" }'

    # Retrieve the response, while overriding shell with 'powershell'
    response = run(cmd,
                   cwd=cwd,
                   stdin=stdin,
                   runas=runas,
                   shell='powershell',
                   env=env,
                   clean_env=clean_env,
                   template=template,
                   rstrip=rstrip,
                   umask=umask,
                   output_encoding=output_encoding,
                   output_loglevel=output_loglevel,
                   hide_output=hide_output,
                   timeout=timeout,
                   reset_system_locale=reset_system_locale,
                   ignore_retcode=ignore_retcode,
                   saltenv=saltenv,
                   use_vt=use_vt,
                   python_shell=python_shell,
                   password=password,
                   encoded_cmd=encoded_cmd,
                   **kwargs)

    try:
        return salt.utils.json.loads(response)
    except Exception:
        log.error("Error converting PowerShell JSON return", exc_info=True)
        return {}