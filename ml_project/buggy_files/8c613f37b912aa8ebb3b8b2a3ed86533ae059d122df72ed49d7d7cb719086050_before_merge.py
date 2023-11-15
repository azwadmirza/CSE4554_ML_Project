def run(name,
        cmd,
        container_type=None,
        exec_driver=None,
        output=None,
        no_start=False,
        stdin=None,
        python_shell=True,
        output_loglevel='debug',
        ignore_retcode=False,
        path=None,
        use_vt=False,
        keep_env=None):
    '''
    Common logic for running shell commands in containers

    path
        path to the container parent (for LXC only)
        default: /var/lib/lxc (system default)

    CLI Example:

    .. code-block:: bash

        salt myminion container_resource.run mycontainer 'ps aux' container_type=docker exec_driver=nsenter output=stdout
    '''
    valid_output = ('stdout', 'stderr', 'retcode', 'all')
    if output is None:
        cmd_func = 'cmd.run'
    elif output not in valid_output:
        raise SaltInvocationError(
            '\'output\' param must be one of the following: {0}'
            .format(', '.join(valid_output))
        )
    else:
        cmd_func = 'cmd.run_all'

    if keep_env is None or isinstance(keep_env, bool):
        to_keep = []
    elif not isinstance(keep_env, (list, tuple)):
        try:
            to_keep = keep_env.split(',')
        except AttributeError:
            log.warning('Invalid keep_env value, ignoring')
            to_keep = []
    else:
        to_keep = keep_env

    if exec_driver == 'lxc-attach':
        full_cmd = 'lxc-attach '
        if path:
            full_cmd += '-P {0} '.format(pipes.quote(path))
        if keep_env is not True:
            full_cmd += '--clear-env '
            if 'PATH' not in to_keep:
                full_cmd += '--set-var {0} '.format(PATH)
                # --clear-env results in a very restrictive PATH
                # (/bin:/usr/bin), use a good fallback.
        full_cmd += ' '.join(
            ['--set-var {0}={1}'.format(x, pipes.quote(os.environ[x]))
                for x in to_keep
                if x in os.environ]
        )
        full_cmd += ' -n {0} -- {1}'.format(pipes.quote(name), cmd)
    elif exec_driver == 'nsenter':
        pid = __salt__['{0}.pid'.format(container_type)](name)
        full_cmd = (
            'nsenter --target {0} --mount --uts --ipc --net --pid -- '
            .format(pid)
        )
        if keep_env is not True:
            full_cmd += 'env -i '
            if 'PATH' not in to_keep:
                full_cmd += '{0} '.format(PATH)
        full_cmd += ' '.join(
            ['{0}={1}'.format(x, pipes.quote(os.environ[x]))
                for x in to_keep
                if x in os.environ]
        )
        full_cmd += ' {0}'.format(cmd)
    elif exec_driver == 'docker-exec':
        # We're using docker exec on the CLI as opposed to via docker-py, since
        # the Docker API doesn't return stdout and stderr separately.
        full_cmd = 'docker exec '
        if stdin:
            full_cmd += '-i '
        full_cmd += '{0} '.format(name)
        if keep_env is not True:
            full_cmd += 'env -i '
            if 'PATH' not in to_keep:
                full_cmd += '{0} '.format(PATH)
        full_cmd += ' '.join(
            ['{0}={1}'.format(x, pipes.quote(os.environ[x]))
                for x in to_keep
                if x in os.environ]
        )
        full_cmd += ' {0}'.format(cmd)

    if not use_vt:
        ret = __salt__[cmd_func](full_cmd,
                                 stdin=stdin,
                                 python_shell=python_shell,
                                 output_loglevel=output_loglevel,
                                 ignore_retcode=ignore_retcode)
    else:
        stdout, stderr = '', ''
        try:
            proc = vt.Terminal(full_cmd,
                               shell=python_shell,
                               log_stdin_level=output_loglevel if
                                               output_loglevel == 'quiet'
                                               else 'info',
                               log_stdout_level=output_loglevel,
                               log_stderr_level=output_loglevel,
                               log_stdout=True,
                               log_stderr=True,
                               stream_stdout=False,
                               stream_stderr=False)
            # Consume output
            while proc.has_unread_data:
                try:
                    cstdout, cstderr = proc.recv()
                    if cstdout:
                        stdout += cstdout
                    if cstderr:
                        if output is None:
                            stdout += cstderr
                        else:
                            stderr += cstderr
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break
            ret = stdout if output is None \
                else {'retcode': proc.exitstatus,
                      'pid': 2,
                      'stdout': stdout,
                      'stderr': stderr}
        except vt.TerminalException:
            trace = traceback.format_exc()
            log.error(trace)
            ret = stdout if output is None \
                else {'retcode': 127,
                      'pid': 2,
                      'stdout': stdout,
                      'stderr': stderr}
        finally:
            proc.terminate()

    return ret