def runner(fun, arg=None, timeout=5):
    '''
    Execute a runner on the master and return the data from the runner
    function

    CLI Example:

    .. code-block:: bash

        salt publish.runner manage.down
    '''
    arg = _parse_args(arg)

    if 'master_uri' not in __opts__:
        return 'No access to master. If using salt-call with --local, please remove.'
    log.info('Publishing runner \'{0}\' to {master_uri}'.format(fun, **__opts__))
    auth = salt.crypt.SAuth(__opts__)
    tok = auth.gen_token('salt')
    load = {'cmd': 'minion_runner',
            'fun': fun,
            'arg': arg,
            'tok': tok,
            'tmo': timeout,
            'id': __opts__['id'],
            'no_parse': __opts__.get('no_parse', [])}

    channel = salt.transport.Channel.factory(__opts__)
    try:
        return channel.send(load)
    except SaltReqTimeoutError:
        return '\'{0}\' runner publish timed out'.format(fun)