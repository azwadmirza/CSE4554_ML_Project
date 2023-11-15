def arp():
    '''
    Return the arp table from the minion

    CLI Example:

    .. code-block:: bash

        salt '*' '*' network.arp
    '''
    ret = {}
    out = __salt__['cmd.run']('arp -an')
    for line in out.splitlines():
        comps = line.split()
        if len(comps) < 4:
            continue
        ret[comps[3]] = comps[1].strip('(').strip(')')
    return ret