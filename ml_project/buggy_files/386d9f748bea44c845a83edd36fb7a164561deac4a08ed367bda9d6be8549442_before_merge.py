def check_password(name, password, runas=None):
    '''
    .. versionadded:: 2016.3.0

    Checks if a user's password is valid.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq.check_password rabbit_user password
    '''
    # try to get the rabbitmq-version - adapted from _get_rabbitmq_plugin

    if runas is None:
        runas = salt.utils.get_user()

    try:
        res = __salt__['cmd.run'](['rabbitmqctl', 'status'], runas=runas, python_shell=False)
        server_version = re.search(r'\{rabbit,"RabbitMQ","(.+)"\}', res)

        if server_version is None:
            raise ValueError

        server_version = server_version.group(1)
        version = [int(i) for i in server_version.split('.')]
    except ValueError:
        version = (0, 0, 0)
    if len(version) < 3:
        version = (0, 0, 0)

    # rabbitmq introduced a native api to check a username and password in version 3.5.7.
    if tuple(version) >= (3, 5, 7):
        res = __salt__['cmd.run'](
            ['rabbitmqctl', 'authenticate_user', name, password],
            runas=runas,
            output_loglevel='quiet',
            python_shell=False)

        return 'Error:' not in res

    cmd = ('rabbit_auth_backend_internal:check_user_login'
        '(<<"{0}">>, [{{password, <<"{1}">>}}]).').format(
        name.replace('"', '\\"'),
        password.replace('"', '\\"'))

    res = __salt__['cmd.run'](
        ['rabbitmqctl', 'eval', cmd],
        runas=runas,
        output_loglevel='quiet',
        python_shell=False)
    msg = 'password-check'

    _response = _format_response(res, msg)
    _key = _response.keys()[0]

    if 'invalid credentials' in _response[_key]:
        return False

    return True