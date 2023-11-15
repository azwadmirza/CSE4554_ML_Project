def insert(name, table='filter', family='ipv4', **kwargs):
    '''
    .. versionadded:: 2014.1.0

    Insert a rule into a chain

    name
        A user-defined name to call this rule by in another part of a state or
        formula. This should not be an actual rule.

    table
        The table that owns the chain that should be modified

    family
        Networking family, either ipv4 or ipv6

    position
        The numerical representation of where the rule should be inserted into
        the chain. Note that ``-1`` is not a supported position value.

    All other arguments are passed in with the same name as the long option
    that would normally be used for iptables, with one exception: ``--state`` is
    specified as `connstate` instead of `state` (not to be confused with
    `ctstate`).

    Jump options that doesn't take arguments should be passed in with an empty
    string.
    '''
    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}

    if 'rules' in kwargs:
        ret['changes']['locale'] = []
        comments = []
        save = False
        for rule in kwargs['rules']:
            if 'rules' in rule:
                del rule['rules']
            if '__agg__' in rule:
                del rule['__agg__']
            if 'save' in rule and rule['save']:
                save = True
                if rule['save'] is not True:
                    save_file = rule['save']
                else:
                    save_file = True
                rule['save'] = False
            _ret = insert(**rule)
            if 'locale' in _ret['changes']:
                ret['changes']['locale'].append(_ret['changes']['locale'])
            comments.append(_ret['comment'])
            ret['result'] = _ret['result']
        if save:
            if save_file is True:
                save_file = None
            __salt__['iptables.save'](save_file, family=family)
        if not ret['changes']['locale']:
            del ret['changes']['locale']
        ret['comment'] = '\n'.join(comments)
        return ret

    for ignore in _STATE_INTERNAL_KEYWORDS:
        if ignore in kwargs:
            del kwargs[ignore]
    kwargs['name'] = name
    kwargs['table'] = table
    rule = __salt__['iptables.build_rule'](family=family, **kwargs)
    command = __salt__['iptables.build_rule'](full=True, family=family, command='I', **kwargs)
    if __salt__['iptables.check'](table,
                                  kwargs['chain'],
                                  rule,
                                  family) is True:
        ret['result'] = True
        ret['comment'] = 'iptables rule for {0} already set for {1} ({2})'.format(
            name,
            family,
            command.strip())
        if 'save' in kwargs and kwargs['save']:
            if kwargs['save'] is not True:
                filename = kwargs['save']
            else:
                filename = None
            saved_rules = __salt__['iptables.get_saved_rules'](family=family)
            _rules = __salt__['iptables.get_rules'](family=family)
            __rules = []
            for table in _rules:
                for chain in _rules[table]:
                    __rules.append(_rules[table][chain].get('rules'))
            __saved_rules = []
            for table in saved_rules:
                for chain in saved_rules[table]:
                    __saved_rules.append(saved_rules[table][chain].get('rules'))
            # Only save if rules in memory are different than saved rules
            if __rules != __saved_rules:
                out = __salt__['iptables.save'](filename, family=family)
                ret['comment'] += ('\nSaved iptables rule {0} for {1}\n'
                                   '{2}\n{3}').format(name, family, command.strip(), out)
        return ret
    if __opts__['test']:
        ret['comment'] = 'iptables rule for {0} needs to be set for {1} ({2})'.format(
            name,
            family,
            command.strip())
        return ret
    if not __salt__['iptables.insert'](table, kwargs['chain'], kwargs['position'], rule, family):
        ret['changes'] = {'locale': name}
        ret['result'] = True
        ret['comment'] = 'Set iptables rule for {0} to: {1} for {2}'.format(
            name,
            command.strip(),
            family)
        if 'save' in kwargs:
            if kwargs['save']:
                out = __salt__['iptables.save'](filename=None, family=family)
                ret['comment'] = ('Set and saved iptables rule {0} for {1}\n'
                                  '{2}\n{3}').format(name, family, command.strip(), out)
        return ret
    else:
        ret['result'] = False
        ret['comment'] = ('Failed to set iptables rule for {0}.\n'
                          'Attempted rule was {1}').format(
                              name,
                              command.strip())
        return ret