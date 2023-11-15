def chain_absent(name, table='filter', family='ipv4'):
    '''
    .. versionadded:: 2014.1.0

    Verify the chain is absent.

    family
        Networking family, either ipv4 or ipv6
    '''

    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}

    chain_check = __salt__['iptables.check_chain'](table, name, family)
    if not chain_check:
        ret['result'] = True
        ret['comment'] = ('iptables {0} chain is already absent in {1} table for {2}'
                          .format(name, table, family))
        return ret
    if __opts__['test']:
        ret['comment'] = 'iptables {0} chain in {1} table needs to be removed {2}'.format(
            name,
            table,
            family)
        return ret
    flush_chain = __salt__['iptables.flush'](table, name, family)
    if not flush_chain:
        command = __salt__['iptables.delete_chain'](table, name, family)
        if command is True:
            ret['changes'] = {'locale': name}
            ret['result'] = True
            ret['comment'] = ('iptables {0} chain in {1} table delete success for {2}'
                              .format(name, table, family))
        else:
            ret['result'] = False
            ret['comment'] = ('Failed to delete {0} chain in {1} table: {2} for {3}'
                              .format(name, table, command.strip(), family))
    else:
        ret['result'] = False
        ret['comment'] = 'Failed to flush {0} chain in {1} table: {2} for {3}'.format(
            name,
            table,
            flush_chain.strip(),
            family
        )
    return ret