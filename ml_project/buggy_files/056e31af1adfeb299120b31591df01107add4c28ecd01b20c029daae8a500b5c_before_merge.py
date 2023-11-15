def call_docker(args, dockeropts, environment):
    executable_path = find_executable('docker')
    if not executable_path:
        raise UserError(errors.docker_not_found_msg("Couldn't find `docker` binary."))

    tls = dockeropts.get('--tls', False)
    ca_cert = dockeropts.get('--tlscacert')
    cert = dockeropts.get('--tlscert')
    key = dockeropts.get('--tlskey')
    verify = dockeropts.get('--tlsverify')
    host = dockeropts.get('--host')
    tls_options = []
    if tls:
        tls_options.append('--tls')
    if ca_cert:
        tls_options.extend(['--tlscacert', ca_cert])
    if cert:
        tls_options.extend(['--tlscert', cert])
    if key:
        tls_options.extend(['--tlskey', key])
    if verify:
        tls_options.append('--tlsverify')
    if host:
        tls_options.extend(
            ['--host', re.sub(r'^https?://', 'tcp://', host.lstrip('='))]
        )

    args = [executable_path] + tls_options + args
    log.debug(" ".join(map(pipes.quote, args)))

    return subprocess.call(args, env=environment)