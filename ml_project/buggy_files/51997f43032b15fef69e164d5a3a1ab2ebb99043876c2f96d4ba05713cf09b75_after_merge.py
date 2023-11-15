def root_cmd(command, tty, sudo, **kwargs):
    '''
    Wrapper for commands to be run as root
    '''
    if sudo:
        if 'sudo_password' in kwargs and kwargs['sudo_password'] is not None:
            command = 'echo "{1}" | sudo -S {0}'.format(
                command,
                kwargs['sudo_password'],
            )
        else:
            command = 'sudo {0}'.format(command)
        log.debug('Using sudo to run command {0}'.format(command))

    ssh_args = []

    if tty:
        # Use double `-t` on the `ssh` command, it's necessary when `sudo` has
        # `requiretty` enforced.
        ssh_args.extend(['-t', '-t'])

    ssh_args.extend([
        # Don't add new hosts to the host key database
        '-oStrictHostKeyChecking=no',
        # Set hosts key database path to /dev/null, ie, non-existing
        '-oUserKnownHostsFile=/dev/null',
        # Don't re-use the SSH connection. Less failures.
        '-oControlPath=none'
    ])

    if 'key_filename' in kwargs:
        # There should never be both a password and an ssh key passed in, so
        ssh_args.extend([
            # tell SSH to skip password authentication
            '-oPasswordAuthentication=no',
            '-oChallengeResponseAuthentication=no',
            # Make sure public key authentication is enabled
            '-oPubkeyAuthentication=yes',
            # No Keyboard interaction!
            '-oKbdInteractiveAuthentication=no',
            # Also, specify the location of the key file
            '-i {0}'.format(kwargs['key_filename'])
        ])

    cmd = 'ssh {0} {1[username]}@{1[hostname]} {2}'.format(
        ' '.join(ssh_args), kwargs, pipes.quote(command)
    )
    log.debug('SSH command: {0!r}'.format(cmd))

    try:
        proc = vt.Terminal(
            cmd,
            shell=True,
            log_stdout=True,
            log_stderr=True,
            stream_stdout=kwargs.get('display_ssh_output', True),
            stream_stderr=kwargs.get('display_ssh_output', True)
        )

        sent_password = False
        while proc.isalive():
            stdout, stderr = proc.recv()
            if stdout and SSH_PASSWORD_PROMP_RE.match(stdout):
                if sent_password:
                    # second time??? Wrong password?
                    log.warning(
                        'Asking for password again. Wrong one provided???'
                    )
                    proc.terminate()
                    return 1

                proc.sendline(kwargs['password'])
                sent_password = True

            time.sleep(0.025)

        proc.close(force=True)
        return proc.exitstatus
    except vt.TerminalException as err:
        log.error(
            'Failed to execute command {0!r}: {1}\n'.format(
                command, err
            ),
            exc_info=True
        )

    # Signal an error
    return 1