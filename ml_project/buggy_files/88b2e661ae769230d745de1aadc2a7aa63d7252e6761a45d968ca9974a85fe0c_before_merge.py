def send(func, *args, **kwargs):
    '''
    Send a specific function to the mine.

    CLI Example:

    .. code-block:: bash

        salt '*' mine.send network.ip_addrs eth0
        salt '*' mine.send eth0_ip_addrs mine_function=network.ip_addrs eth0
    '''
    mine_func = kwargs.pop('mine_function', func)
    if mine_func not in __salt__:
        return False
    data = {}
    arg_data = salt.utils.arg_lookup(__salt__[mine_func])
    func_data = copy.deepcopy(kwargs)
    for ind, _ in enumerate(arg_data.get('args', [])):
        try:
            func_data[arg_data['args'][ind]] = args[ind]
        except IndexError:
            # Safe error, arg may be in kwargs
            pass
    f_call = salt.utils.format_call(__salt__[mine_func],
                                    func_data,
                                    expected_extra_kws=MINE_INTERNAL_KEYWORDS)
    for arg in args:
        if arg not in f_call['args']:
            f_call['args'].append(arg)
    try:
        if 'kwargs' in f_call:
            data[func] = __salt__[mine_func](*f_call['args'], **f_call['kwargs'])
        else:
            data[func] = __salt__[mine_func](*f_call['args'])
    except Exception as exc:
        log.error('Function {0} in mine.send failed to execute: {1}'
                  .format(mine_func, exc))
        return False
    if __opts__['file_client'] == 'local':
        old = __salt__['data.getval']('mine_cache')
        if isinstance(old, dict):
            old.update(data)
            data = old
        return __salt__['data.update']('mine_cache', data)
    load = {
            'cmd': '_mine',
            'data': data,
            'id': __opts__['id'],
    }
    return _mine_send(load, __opts__)