def running(name,
            restart=False,
            update=False,
            runas=None,
            conf_file=None,
            bin_env=None
        ):
    '''
    Ensure the named service is running.

    name
        Service name as defined in the supervisor configuration file
    restart
        Whether to force a restart
    update
        Whether to update the supervisor configuration.
    runas
        Name of the user to run the supervisorctl command
    conf_file
        path to supervisorctl config file
    bin_env
        path to supervisorctl bin or path to virtualenv with supervisor installed

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    all_processes = __salt__['supervisord.status'](
        user=runas,
        conf_file=conf_file,
        bin_env=bin_env
    )
    needs_update = name not in all_processes

    if __opts__['test']:
        ret['result'] = None
        _msg = 'restarted' if restart else 'started'
        _update = ', but service needs to be added' if needs_update else ''
        ret['comment'] = (
            'Service {0} is set to be {1}{2}'.format(
                name, _msg, _update))
        return ret

    changes = []
    just_updated = False
    if needs_update:
        comment = 'Adding service: {0}'.format(name)
        __salt__['supervisord.reread'](
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env
        )
        result = __salt__['supervisord.add'](
            name,
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env
        )

        ret.update(_check_error(result, comment))
        changes.append(comment)
        log.debug(comment)

    elif update:
        comment = 'Updating supervisor'
        result = __salt__['supervisord.update'](
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env
        )
        ret.update(_check_error(result, comment))
        changes.append(comment)
        log.debug(comment)

        if '{0}: updated'.format(name) in result:
            just_updated = True

    if name in all_processes and not _is_stopped_state(all_processes[name]['state']):
        if restart and not just_updated:
            comment = 'Restarting service: {0}'.format(name)
            log.debug(comment)
            result = __salt__['supervisord.restart'](
                name,
                user=runas,
                conf_file=conf_file,
                bin_env=bin_env
            )
            ret.update(_check_error(result, comment))
            changes.append(comment)
        elif just_updated:
            comment = 'Not starting updated service: {0}'.format(name)
            result = comment
            ret.update({'comment': comment})
        else:
            comment = 'Not starting already running service: {0}'.format(name)
            result = comment
            ret.update({'comment': comment})
    elif not just_updated:
        comment = 'Starting service: {0}'.format(name)
        changes.append(comment)
        log.debug(comment)
        result = __salt__['supervisord.start'](
            name,
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env
        )

        ret.update(_check_error(result, comment))
        log.debug(unicode(result))
    if ret['result'] and len(changes):
        ret['changes'][name] = ' '.join(changes)
    return ret