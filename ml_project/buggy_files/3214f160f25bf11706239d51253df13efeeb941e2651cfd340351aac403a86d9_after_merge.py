def _git_run(command, cwd=None, runas=None, identity=None,
             ignore_retcode=False, failhard=True, redirect_stderr=False,
             **kwargs):
    '''
    simple, throw an exception with the error message on an error return code.

    this function may be moved to the command module, spliced with
    'cmd.run_all', and used as an alternative to 'cmd.run_all'. Some
    commands don't return proper retcodes, so this can't replace 'cmd.run_all'.
    '''
    env = {}

    if identity:
        _salt_cli = __opts__.get('__cli', '')
        errors = []
        missing_keys = []

        # if the statefile provides multiple identities, they need to be tried
        # (but also allow a string instead of a list)
        if not isinstance(identity, list):
            # force it into a list
            identity = [identity]

        # try each of the identities, independently
        for id_file in identity:
            if not os.path.isfile(id_file):
                missing_keys.append(id_file)
                log.warning('Identity file {0} does not exist'.format(id_file))
                continue

            env = {
                'GIT_IDENTITY': id_file
            }

            # copy wrapper to area accessible by ``runas`` user
            # currently no suppport in windows for wrapping git ssh
            ssh_id_wrapper = os.path.join(
                salt.utils.templates.TEMPLATE_DIRNAME,
                'git/ssh-id-wrapper'
            )
            if salt.utils.is_windows():
                for suffix in ('', ' (x86)'):
                    ssh_exe = (
                        'C:\\Program Files{0}\\Git\\bin\\ssh.exe'
                        .format(suffix)
                    )
                    if os.path.isfile(ssh_exe):
                        env['GIT_SSH_EXE'] = ssh_exe
                        break
                else:
                    raise CommandExecutionError(
                        'Failed to find ssh.exe, unable to use identity file'
                    )
                # Use the windows batch file instead of the bourne shell script
                ssh_id_wrapper += '.bat'
                env['GIT_SSH'] = ssh_id_wrapper
            else:
                tmp_file = salt.utils.mkstemp()
                salt.utils.files.copyfile(ssh_id_wrapper, tmp_file)
                os.chmod(tmp_file, 0o500)
                os.chown(tmp_file, __salt__['file.user_to_uid'](runas), -1)
                env['GIT_SSH'] = tmp_file

            if 'salt-call' not in _salt_cli \
                    and __salt__['ssh.key_is_encrypted'](id_file):
                errors.append(
                    'Identity file {0} is passphrase-protected and cannot be '
                    'used in a non-interactive command. Using salt-call from '
                    'the minion will allow a passphrase-protected key to be '
                    'used.'.format(id_file)
                )
                continue

            log.info(
                'Attempting git authentication using identity file {0}'
                .format(id_file)
            )

            try:
                result = __salt__['cmd.run_all'](
                    command,
                    cwd=cwd,
                    runas=runas,
                    env=env,
                    python_shell=False,
                    log_callback=salt.utils.url.redact_http_basic_auth,
                    ignore_retcode=ignore_retcode,
                    redirect_stderr=redirect_stderr,
                    **kwargs)
            finally:
                if not salt.utils.is_windows() and 'GIT_SSH' in env:
                    os.remove(env['GIT_SSH'])

            # If the command was successful, no need to try additional IDs
            if result['retcode'] == 0:
                return result
            else:
                err = result['stdout' if redirect_stderr else 'stderr']
                if err:
                    errors.append(salt.utils.url.redact_http_basic_auth(err))

        # We've tried all IDs and still haven't passed, so error out
        if failhard:
            msg = (
                'Unable to authenticate using identity file:\n\n{0}'.format(
                    '\n'.join(errors)
                )
            )
            if missing_keys:
                if errors:
                    msg += '\n\n'
                msg += (
                    'The following identity file(s) were not found: {0}'
                    .format(', '.join(missing_keys))
                )
            raise CommandExecutionError(msg)
        return result

    else:
        result = __salt__['cmd.run_all'](
            command,
            cwd=cwd,
            runas=runas,
            env=env,
            python_shell=False,
            log_callback=salt.utils.url.redact_http_basic_auth,
            ignore_retcode=ignore_retcode,
            redirect_stderr=redirect_stderr,
            **kwargs)

        if result['retcode'] == 0:
            return result
        else:
            if failhard:
                gitcommand = ' '.join(command) \
                    if isinstance(command, list) \
                    else command
                msg = 'Command \'{0}\' failed'.format(
                    salt.utils.url.redact_http_basic_auth(gitcommand)
                )
                err = result['stdout' if redirect_stderr else 'stderr']
                if err:
                    msg += ': {0}'.format(
                        salt.utils.url.redact_http_basic_auth(err)
                    )
                raise CommandExecutionError(msg)
            return result