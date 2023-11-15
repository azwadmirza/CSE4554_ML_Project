def present(name,
            pattern,
            definition,
            apply_to=None,
            priority=0,
            vhost='/',
            runas=None):
    '''
    Ensure the RabbitMQ policy exists.

    Reference: http://www.rabbitmq.com/ha.html

    name
        Policy name
    pattern
        A regex of queues to apply the policy to
    definition
        A json dict describing the policy
    priority
        Priority (defaults to 0)
    apply_to
        Apply policy to 'queues', 'exchanges' or 'all' (default to 'all')
    vhost
        Virtual host to apply to (defaults to '/')
    runas
        Name of the user to run the command as
    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}
    result = {}

    policies = __salt__['rabbitmq.list_policies'](vhost=vhost, runas=runas)
    policy = policies.get(vhost, {}).get(name)
    updates = []
    if policy:
        if policy.get('pattern') != pattern:
            updates.append('Pattern')
        if policy.get('definition') != definition:
            updates.append('Definition')
        if apply_to and (policy.get('apply-to') != apply_to):
            updates.append('Applyto')
        if int(policy.get('priority')) != priority:
            updates.append('Priority')

    if policy and not updates:
        ret['comment'] = 'Policy {0} {1} is already present'.format(vhost, name)
        return ret

    if not policy:
        ret['changes'].update({'old': {}, 'new': name})
        if __opts__['test']:
            ret['comment'] = 'Policy {0} {1} is set to be created'.format(vhost, name)
        else:
            log.debug('Policy doesn\'t exist - Creating')
            result = __salt__['rabbitmq.set_policy'](vhost,
                                                     name,
                                                     pattern,
                                                     definition,
                                                     apply_to,
                                                     priority=priority,
                                                     runas=runas)
    elif updates:
        ret['changes'].update({'old': policy, 'new': updates})
        if __opts__['test']:
            ret['comment'] = 'Policy {0} {1} is set to be updated'.format(vhost, name)
        else:
            log.debug('Policy exists but needs updating')
            result = __salt__['rabbitmq.set_policy'](vhost,
                                                     name,
                                                     pattern,
                                                     definition,
                                                     apply_to,
                                                     priority=priority,
                                                     runas=runas)

    if 'Error' in result:
        ret['result'] = False
        ret['comment'] = result['Error']
    elif ret['changes'] == {}:
        ret['comment'] = '\'{0}\' is already in the desired state.'.format(name)
    elif __opts__['test']:
        ret['result'] = None
    elif 'Set' in result:
        ret['comment'] = result['Set']

    return ret