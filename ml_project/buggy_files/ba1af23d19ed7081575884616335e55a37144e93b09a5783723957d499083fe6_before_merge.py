def set_policy(vhost, name, pattern, definition, priority=None, apply_to=None, runas=None):
    '''
    Set a policy based on rabbitmqctl set_policy.

    Reference: http://www.rabbitmq.com/ha.html

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq.set_policy / HA '.*' '{"ha-mode":"all"}'
    '''
    if runas is None and not salt.utils.platform.is_windows():
        runas = salt.utils.user.get_user()
    if isinstance(definition, dict):
        definition = salt.utils.json.dumps(definition)
    if not isinstance(definition, six.string_types):
        raise SaltInvocationError(
            'The \'definition\' argument must be a dictionary or JSON string'
        )
    cmd = [RABBITMQCTL, 'set_policy', '-p', vhost]
    if priority:
        cmd.extend(['--priority', priority])
    if apply_to:
        cmd.extend(['--apply-to', apply_to])
    cmd.extend([name, pattern, definition])
    res = __salt__['cmd.run_all'](cmd, runas=runas, python_shell=False)
    log.debug('Set policy: %s', res['stdout'])
    return _format_response(res, 'Set')