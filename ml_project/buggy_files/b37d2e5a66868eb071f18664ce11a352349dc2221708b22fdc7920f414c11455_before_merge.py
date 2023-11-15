def scp_file(dest_path, contents, kwargs):
    '''
    Use scp to copy a file to a server
    '''
    tmpfh, tmppath = tempfile.mkstemp()
    with salt.utils.fopen(tmppath, 'w') as tmpfile:
        tmpfile.write(contents)

    log.debug('Uploading {0} to {1} (scp)'.format(dest_path, kwargs['hostname']))

    ssh_args = [
        # Don't add new hosts to the host key database
        '-oStrictHostKeyChecking=no',
        # Set hosts key database path to /dev/null, ie, non-existing
        '-oUserKnownHostsFile=/dev/null',
        # Don't re-use the SSH connection. Less failures.
        '-oControlPath=none'
    ]
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

    cmd = 'scp {0} {1} {2[username]}@{2[hostname]}:{3}'.format(
        ' '.join(ssh_args), tmppath, kwargs, dest_path
    )
    log.debug('SCP command: {0!r}'.format(cmd))

    try:
        proc = vt.Terminal(
            cmd,
            shell=True,
            log_stdout=True,
            log_stderr=True,
            stream_stdout=kwargs.get('display_ssh_output', True),
            stream_stderr=kwargs.get('display_ssh_output', True)
        )
        log.debug('Uploading file(PID {0}): {1!r}'.format(proc.pid, dest_path))

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

        return proc.exitstatus
    except vt.TerminalException as err:
        log.error(
            'Failed to upload file {0!r}: {1}\n'.format(
                dest_path, err
            ),
            exc_info=True
        )

    # Signal an error
    return 1