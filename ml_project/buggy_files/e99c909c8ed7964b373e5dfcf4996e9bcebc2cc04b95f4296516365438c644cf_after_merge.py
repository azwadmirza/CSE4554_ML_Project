def _exec_ssh_cmd(cmd, error_msg=None, allow_failure=False, **kwargs):
    if error_msg is None:
        error_msg = 'A wrong password has been issued while establishing ssh session.'
    password_retries = kwargs.get('password_retries', 3)
    try:
        stdout, stderr = None, None
        proc = vt.Terminal(
            cmd,
            shell=True,
            log_stdout=True,
            log_stderr=True,
            stream_stdout=kwargs.get('display_ssh_output', True),
            stream_stderr=kwargs.get('display_ssh_output', True)
        )
        sent_password = 0
        while proc.has_unread_data:
            stdout, stderr = proc.recv()
            if stdout and SSH_PASSWORD_PROMP_RE.search(stdout):
                # if authenticating with an SSH key and 'sudo' is found
                # in the password prompt
                if ('key_filename' in kwargs and kwargs['key_filename']
                    and SSH_PASSWORD_PROMP_SUDO_RE.search(stdout)
                ):
                    proc.sendline(kwargs['sudo_password'])
                # elif authenticating via password and haven't exhausted our
                # password_retires
                elif (
                            kwargs.get('password', None)
                        and (sent_password < password_retries)
                ):
                    sent_password += 1
                    proc.sendline(kwargs['password'])
                # else raise an error as we are not authenticating properly
                #  * not authenticating with an SSH key
                #  * not authenticating with a Password
                else:
                    raise SaltCloudPasswordError(error_msg)
            # 0.0125 is really too fast on some systems
            time.sleep(0.5)
        if proc.exitstatus != 0 and allow_failure is False:
            raise SaltCloudSystemExit(
                'Command \'{0}\' failed. Exit code: {1}'.format(
                    cmd, proc.exitstatus
                )
            )
        return proc.exitstatus
    except vt.TerminalException as err:
        trace = traceback.format_exc()
        log.error(error_msg.format(cmd, err, trace))
    finally:
        proc.close(terminate=True, kill=True)
    # Signal an error
    return 1