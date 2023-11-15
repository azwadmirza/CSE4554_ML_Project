def flush(name, family='ipv4', **kwargs):
    '''
    .. versionadded:: 2014.1.0

    Flush current iptables state

    family
        Networking family, either ipv4 or ipv6

    '''
    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}

    for ignore in _STATE_INTERNAL_KEYWORDS:
        if ignore in kwargs:
            del kwargs[ignore]

    if 'table' not in kwargs:
        kwargs['table'] = 'filter'

    if 'chain' not in kwargs:
        kwargs['chain'] = ''
    if __opts__['test']:
        ret['comment'] = 'iptables rules in {0} table {1} chain {2} family needs to be flushed'.format(
            name,
            kwargs['table'],
            family)
        return ret
    if not __salt__['iptables.flush'](kwargs['table'], kwargs['chain'], family):
        ret['changes'] = {'locale': name}
        ret['result'] = True
        ret['comment'] = 'Flush iptables rules in {0} table {1} chain {2} family'.format(
            kwargs['table'],
            kwargs['chain'],
            family
        )
        return ret
    else:
        ret['result'] = False
        ret['comment'] = 'Failed to flush iptables rules'
        return ret