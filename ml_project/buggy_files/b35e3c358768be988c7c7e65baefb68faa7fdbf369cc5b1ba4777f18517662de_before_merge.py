def _psql_cmd(*args, **kwargs):
    '''
    Return string with fully composed psql command.

    Accept optional keyword arguments: user, host and port as well as any
    number or positional arguments to be added to the end of command.
    '''
    (user, host, port, maintenance_db, password) = _connection_defaults(
        kwargs.get('user'),
        kwargs.get('host'),
        kwargs.get('port'),
        kwargs.get('maintenance_db'),
        kwargs.get('password'))

    cmd = [salt.utils.which('psql'),
           '--no-align',
           '--no-readline',
           '--no-password']  # It is never acceptable to issue a password prompt.
    if user:
        cmd += ['--username', user]
    if host:
        cmd += ['--host', host]
    if port:
        cmd += ['--port', str(port)]
    if not maintenance_db:
        maintenance_db = 'postgres'
    cmd.extend(['--dbname', maintenance_db])
    cmd.extend(args)
    return cmd