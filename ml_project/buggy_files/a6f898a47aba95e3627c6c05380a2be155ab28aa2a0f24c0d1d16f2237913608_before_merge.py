def run(cmd,
        cwd=None,
        stdin=None,
        runas=None,
        shell=DEFAULT_SHELL,
        python_shell=None,
        env=None,
        clean_env=False,
        template=None,
        rstrip=True,
        umask=None,
        output_loglevel='debug',
        timeout=None,
        reset_system_locale=True,
        ignore_retcode=False,
        saltenv='base',
        use_vt=False,
        **kwargs):
    '''
    Execute the passed command and return the output as a string

    Note that ``env`` represents the environment variables for the command, and
    should be formatted as a dict, or a YAML string which resolves to a dict.

    *************************************************************************
    WARNING: This function does not process commands through a shell
    unless the python_shell flag is set to True. This means that any
    shell-specific functionality such as 'echo' or the use of pipes,
    redirection or &&, should either be migrated to cmd.shell or
    have the python_shell=True flag set here.

    The use of python_shell=True means that the shell will accept _any_ input
    including potentially malicious commands such as 'good_command;rm -rf /'.
    Be absolutely certain that you have sanitized your input prior to using
    python_shell=True
    *************************************************************************

    CLI Example:

    .. code-block:: bash

        salt '*' cmd.run "ls -l | awk '/foo/{print \\$2}'"

    The template arg can be set to 'jinja' or another supported template
    engine to render the command arguments before execution.
    For example:

    .. code-block:: bash

        salt '*' cmd.run template=jinja "ls -l /tmp/{{grains.id}} | awk '/foo/{print \\$2}'"

    Specify an alternate shell with the shell parameter:

    .. code-block:: bash

        salt '*' cmd.run "Get-ChildItem C:\\ " shell='powershell'

    A string of standard input can be specified for the command to be run using
    the ``stdin`` parameter. This can be useful in cases where sensitive
    information must be read from standard input.:

    .. code-block:: bash

        salt '*' cmd.run "grep f" stdin='one\\ntwo\\nthree\\nfour\\nfive\\n'

    If an equal sign (``=``) appears in an argument to a Salt command it is
    interpreted as a keyword argument in the format ``key=val``. That
    processing can be bypassed in order to pass an equal sign through to the
    remote shell command by manually specifying the kwarg:

    .. code-block:: bash

        salt '*' cmd.run cmd='sed -e s/=/:/g'
    '''
    try:
        if __opts__.get('cmd_safe', True) is False and python_shell is None:
            # Override-switch for python_shell
            python_shell = True
    except NameError:
        pass
    ret = _run(cmd,
               runas=runas,
               shell=shell,
               python_shell=python_shell,
               cwd=cwd,
               stdin=stdin,
               stderr=subprocess.STDOUT,
               env=env,
               clean_env=clean_env,
               template=template,
               rstrip=rstrip,
               umask=umask,
               output_loglevel=output_loglevel,
               timeout=timeout,
               reset_system_locale=reset_system_locale,
               saltenv=saltenv,
               use_vt=use_vt)

    if 'pid' in ret and '__pub_jid' in kwargs:
        # Stuff the child pid in the JID file
        proc_dir = os.path.join(__opts__['cachedir'], 'proc')
        jid_file = os.path.join(proc_dir, kwargs['__pub_jid'])
        if os.path.isfile(jid_file):
            serial = salt.payload.Serial(__opts__)
            with salt.utils.fopen(jid_file, 'rb') as fn_:
                jid_dict = serial.load(fn_)

            if 'child_pids' in jid_dict:
                jid_dict['child_pids'].append(ret['pid'])
            else:
                jid_dict['child_pids'] = [ret['pid']]
            # Rewrite file
            with salt.utils.fopen(jid_file, 'w+b') as fn_:
                fn_.write(serial.dumps(jid_dict))

    lvl = _check_loglevel(output_loglevel)
    if lvl is not None:
        if not ignore_retcode and ret['retcode'] != 0:
            if lvl < LOG_LEVELS['error']:
                lvl = LOG_LEVELS['error']
            log.error(
                'Command {0!r} failed with return code: {1}'
                .format(cmd, ret['retcode'])
            )
        log.log(lvl, 'output: {0}'.format(ret['stdout']))
    return ret['stdout']