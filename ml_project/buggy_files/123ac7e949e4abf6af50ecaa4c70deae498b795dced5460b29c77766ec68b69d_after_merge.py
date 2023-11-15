def wait_for_port(host, port=22, timeout=900, gateway=None):
    '''
    Wait until a connection to the specified port can be made on a specified
    host. This is usually port 22 (for SSH), but in the case of Windows
    installations, it might be port 445 (for winexe). It may also be an
    alternate port for SSH, depending on the base image.
    '''
    start = time.time()
    # Assign test ports because if a gateway is defined
    # we first want to test the gateway before the host.
    test_ssh_host = host
    test_ssh_port = port
    if gateway:
        ssh_gateway = gateway['ssh_gateway']
        ssh_gateway_port = 22
        if ':' in ssh_gateway:
            ssh_gateway, ssh_gateway_port = ssh_gateway.split(':')
        if 'ssh_gateway_port' in gateway:
            ssh_gateway_port = gateway['ssh_gateway_port']
        test_ssh_host = ssh_gateway
        test_ssh_port = ssh_gateway_port
        log.debug(
            'Attempting connection to host {0} on port {1} '
            'via gateway {2} on port {3}'.format(
                host, port, ssh_gateway, ssh_gateway_port
            )
        )
    else:
        log.debug(
            'Attempting connection to host {0} on port {1}'.format(
                host, port
            )
        )
    trycount = 0
    while True:
        trycount += 1
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((test_ssh_host, int(test_ssh_port)))
            # Stop any remaining reads/writes on the socket
            sock.shutdown(socket.SHUT_RDWR)
            # Close it!
            sock.close()
            break
        except socket.error as exc:
            log.debug('Caught exception in wait_for_port: {0}'.format(exc))
            time.sleep(1)
            if time.time() - start > timeout:
                log.error('Port connection timed out: {0}'.format(timeout))
                return False
            if not gateway:
                log.debug(
                    'Retrying connection to host {0} on port {1} '
                    '(try {2})'.format(
                        test_ssh_host, test_ssh_port, trycount
                    )
                )
            else:
                log.debug(
                    'Retrying connection to Gateway {0} on port {1} '
                    '(try {2})'.format(
                        test_ssh_host, test_ssh_port, trycount
                    )
                )
    if not gateway:
        return True
    # Let the user know that his gateway is good!
    log.debug(
        'Gateway {0} on port {1} '
        'is reachable.'.format(
            test_ssh_host, test_ssh_port
        )
    )

    # Now we need to test the host via the gateway.
    # We will use netcat on the gateway to test the port
    ssh_args = []
    ssh_args.extend([
        # Don't add new hosts to the host key database
        '-oStrictHostKeyChecking=no',
        # Set hosts key database path to /dev/null, i.e., non-existing
        '-oUserKnownHostsFile=/dev/null',
        # Don't re-use the SSH connection. Less failures.
        '-oControlPath=none'
    ])
    # There should never be both a password and an ssh key passed in, so
    if 'ssh_gateway_key' in gateway:
        ssh_args.extend([
            # tell SSH to skip password authentication
            '-oPasswordAuthentication=no',
            '-oChallengeResponseAuthentication=no',
            # Make sure public key authentication is enabled
            '-oPubkeyAuthentication=yes',
            # No Keyboard interaction!
            '-oKbdInteractiveAuthentication=no',
            # Also, specify the location of the key file
            '-i {0}'.format(gateway['ssh_gateway_key'])
        ])
    # Netcat command testing remote port
    command = 'nc -z -w5 -q0 {0} {1}'.format(host, port)
    # SSH command
    pcmd = 'ssh {0} {1}@{2} -p {3} {4}'.format(
        ' '.join(ssh_args), gateway['ssh_gateway_user'], ssh_gateway,
        ssh_gateway_port, pipes.quote('date')
    )
    cmd = 'ssh {0} {1}@{2} -p {3} {4}'.format(
        ' '.join(ssh_args), gateway['ssh_gateway_user'], ssh_gateway,
        ssh_gateway_port, pipes.quote(command)
    )
    log.debug('SSH command: {0!r}'.format(cmd))

    kwargs = {'display_ssh_output': False,
              'password': gateway.get('ssh_gateway_password', None)}
    trycount = 0
    usable_gateway = False
    gateway_retries = 5
    while True:
        trycount += 1
        # test gateway usage
        if not usable_gateway:
            pstatus = _exec_ssh_cmd(pcmd, allow_failure=True, **kwargs)
            if pstatus == 0:
                usable_gateway = True
            else:
                gateway_retries -= 1
                log.error(
                    'Gateway usage seems to be broken, '
                    'password error ? Tries left: {0}'.format(gateway_retries))
            if not gateway_retries:
                raise SaltCloudExecutionFailure(
                    'SSH gateway is reachable but we can not login')
        # then try to reach out the target
        if usable_gateway:
            status = _exec_ssh_cmd(cmd, allow_failure=True, **kwargs)
            # Get the exit code of the SSH command.
            # If 0 then the port is open.
            if status == 0:
                return True
        time.sleep(1)
        if time.time() - start > timeout:
            log.error('Port connection timed out: {0}'.format(timeout))
            return False
        log.debug(
            'Retrying connection to host {0} on port {1} '
            'via gateway {2} on port {3}. (try {4})'.format(
                host, port, ssh_gateway, ssh_gateway_port,
                trycount
            )
        )