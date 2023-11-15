def sftp_file(dest_path, contents=None, kwargs=None, local_file=None):
    '''
    Use sftp to upload a file to a server
    '''
    put_args = []

    if kwargs is None:
        kwargs = {}

    file_to_upload = None
    try:
        if contents is not None:
            try:
                tmpfd, file_to_upload = tempfile.mkstemp()
                if isinstance(contents, str):
                    os.write(tmpfd, contents.encode(__salt_system_encoding__))
                else:
                    os.write(tmpfd, contents)
            finally:
                try:
                    os.close(tmpfd)
                except OSError as exc:
                    if exc.errno != errno.EBADF:
                        raise exc

        if local_file is not None:
            file_to_upload = local_file
            if os.path.isdir(local_file):
                put_args = ['-r']

        log.debug('Uploading {0} to {1} (sftp)'.format(dest_path, kwargs.get('hostname')))

        ssh_args = [
            # Don't add new hosts to the host key database
            '-oStrictHostKeyChecking=no',
            # Set hosts key database path to /dev/null, i.e., non-existing
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
                # do only use the provided identity file
                '-oIdentitiesOnly=yes',
                # No Keyboard interaction!
                '-oKbdInteractiveAuthentication=no',
                # Also, specify the location of the key file
                '-oIdentityFile={0}'.format(kwargs['key_filename'])
            ])

        if 'port' in kwargs:
            ssh_args.append('-oPort={0}'.format(kwargs['port']))

        if 'ssh_gateway' in kwargs:
            ssh_gateway = kwargs['ssh_gateway']
            ssh_gateway_port = 22
            ssh_gateway_key = ''
            ssh_gateway_user = 'root'
            if ':' in ssh_gateway:
                ssh_gateway, ssh_gateway_port = ssh_gateway.split(':')
            if 'ssh_gateway_port' in kwargs:
                ssh_gateway_port = kwargs['ssh_gateway_port']
            if 'ssh_gateway_key' in kwargs:
                ssh_gateway_key = '-i {0}'.format(kwargs['ssh_gateway_key'])
            if 'ssh_gateway_user' in kwargs:
                ssh_gateway_user = kwargs['ssh_gateway_user']

            ssh_args.append(
                # Setup ProxyCommand
                '-oProxyCommand="ssh {0} {1} {2} {3} {4}@{5} -p {6} nc -q0 %h %p"'.format(
                    # Don't add new hosts to the host key database
                    '-oStrictHostKeyChecking=no',
                    # Set hosts key database path to /dev/null, i.e., non-existing
                    '-oUserKnownHostsFile=/dev/null',
                    # Don't re-use the SSH connection. Less failures.
                    '-oControlPath=none',
                    ssh_gateway_key,
                    ssh_gateway_user,
                    ssh_gateway,
                    ssh_gateway_port
                )
            )

        try:
            if socket.inet_pton(socket.AF_INET6, kwargs['hostname']):
                ipaddr = '[{0}]'.format(kwargs['hostname'])
            else:
                ipaddr = kwargs['hostname']
        except socket.error:
            ipaddr = kwargs['hostname']

        if file_to_upload is None:
            log.warning(
                'No source file to upload. Please make sure that either file '
                'contents or the path to a local file are provided.'
            )
        cmd = 'echo "put {0} {1} {2}" | sftp {3} {4[username]}@{5}'.format(
            ' '.join(put_args), file_to_upload, dest_path, ' '.join(ssh_args), kwargs, ipaddr
        )
        log.debug('SFTP command: \'{0}\''.format(cmd))
        retcode = _exec_ssh_cmd(cmd,
                                error_msg='Failed to upload file \'{0}\': {1}\n{2}',
                                password_retries=3,
                                **kwargs)
    finally:
        if contents is not None:
            try:
                os.remove(file_to_upload)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    raise exc
    return retcode