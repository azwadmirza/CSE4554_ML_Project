def delete(name, family='ipv4', **kwargs):
    '''
    .. versionadded:: 2014.1.0

    Delete a rule to a chain

    name
        A user-defined name to call this rule by in another part of a state or
        formula. This should not be an actual rule.

    family
        Networking family, either ipv4 or ipv6

    All other arguments are passed in with the same name as the long option
    that would normally be used for iptables, with one exception: ``--state`` is
    specified as `connstate` instead of `state` (not to be confused with
    `ctstate`).
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
                if rule['save'] is not True:
                    save_file = rule['save']
                else:
                    save_file = True
                rule['save'] = False
            _ret = delete(**rule)
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
    rule = __salt__['iptables.build_rule'](family=family, **kwargs)
    command = __salt__['iptables.build_rule'](full=True, family=family, command='D', **kwargs)
    if not __salt__['iptables.check'](kwargs['table'],
                                      kwargs['chain'],
                                      rule,
                                      family) is True:
        ret['result'] = True
        ret['comment'] = 'iptables rule for {0} already absent for {1} ({2})'.format(
            name,
            family,
            command.strip())
        return ret
    if __opts__['test']:
        ret['comment'] = 'iptables rule for {0} needs to be deleted for {1} ({2})'.format(
            name,
            family,
            command.strip())
        return ret

    if 'position' in kwargs:
        result = __salt__['iptables.delete'](
                kwargs['table'],
                kwargs['chain'],
                family=family,
                position=kwargs['position'])
    else:
        result = __salt__['iptables.delete'](
                kwargs['table'],
                kwargs['chain'],
                family=family,
                rule=rule)

    if not result:
        ret['changes'] = {'locale': name}
        ret['result'] = True
        ret['comment'] = 'Delete iptables rule for {0} {1}'.format(
            name,
            command.strip())
        if 'save' in kwargs:
            if kwargs['save']:
                __salt__['iptables.save'](filename=None, family=family)
                ret['comment'] = ('Deleted and Saved iptables rule for {0} for {1}'
                                  '{2}'.format(name, command.strip(), family))
        return ret
    else:
        ret['result'] = False
        ret['comment'] = ('Failed to delete iptables rule for {0}.\n'
                          'Attempted rule was {1}').format(
                              name,
                              command.strip())
        return ret