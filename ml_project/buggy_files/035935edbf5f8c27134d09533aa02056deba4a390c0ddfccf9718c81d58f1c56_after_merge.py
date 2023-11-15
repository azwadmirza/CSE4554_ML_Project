def set_policy(name, table='filter', family='ipv4', **kwargs):
    '''
    .. versionadded:: 2014.1.0

    Sets the default policy for iptables firewall tables

    table
        The table that owns the chain that should be modified

    family
        Networking family, either ipv4 or ipv6

    policy
        The requested table policy

    '''
    ret = {'name': name,
        'changes': {},
        'result': None,
        'comment': ''}

    for ignore in _STATE_INTERNAL_KEYWORDS:
        if ignore in kwargs:
            del kwargs[ignore]

    if __salt__['iptables.get_policy'](
            table,
            kwargs['chain'],
            family) == kwargs['policy']:
        ret['result'] = True
        ret['comment'] = ('iptables default policy for chain {0} on table {1} for {2} already set to {3}'
                          .format(kwargs['chain'], table, family, kwargs['policy']))
        return ret
    if __opts__['test']:
        ret['comment'] = 'iptables default policy for chain {0} on table {1} for {2} needs to be set to {3}'.format(
            kwargs['chain'],
            table,
            family,
            kwargs['policy']
        )
        return ret
    if not __salt__['iptables.set_policy'](
            table,
            kwargs['chain'],
            kwargs['policy'],
            family):
        ret['changes'] = {'locale': name}
        ret['result'] = True
        ret['comment'] = 'Set default policy for {0} to {1} family {2}'.format(
            kwargs['chain'],
            kwargs['policy'],
            family
        )
        if 'save' in kwargs:
            if kwargs['save']:
                __salt__['iptables.save'](filename=None, family=family)
                ret['comment'] = 'Set and Saved default policy for {0} to {1} family {2}'.format(
                    kwargs['chain'],
                    kwargs['policy'],
                    family
                )
        return ret
    else:
        ret['result'] = False
        ret['comment'] = 'Failed to set iptables default policy'
        return ret