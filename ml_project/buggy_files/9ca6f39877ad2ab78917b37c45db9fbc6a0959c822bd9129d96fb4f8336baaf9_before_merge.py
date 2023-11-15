def dead(name,
         user=None,
         runas=None,
         conf_file=None,
         bin_env=None):
    '''
    Ensure the named service is dead (not running).

    name
        Service name as defined in the supervisor configuration file

    runas
        Name of the user to run the supervisorctl command

        .. deprecated:: 0.17.0

    user
        Name of the user to run the supervisorctl command

        .. versionadded:: 0.17.0

    conf_file
        path to supervisorctl config file

    bin_env
        path to supervisorctl bin or path to virtualenv with supervisor
        installed

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    salt.utils.warn_until(
        (0, 18),
        'Please remove \'runas\' support at this stage. \'user\' support was '
        'added in 0.17.0',
        _dont_call_warnings=True
    )
    if runas:
        # Warn users about the deprecation
        ret.setdefault('warnings', []).append(
            'The \'runas\' argument is being deprecated in favor or \'user\', '
            'please update your state files.'
        )
    if user is not None and runas is not None:
        # user wins over runas but let warn about the deprecation.
        ret.setdefault('warnings', []).append(
            'Passed both the \'runas\' and \'user\' arguments. Please don\'t. '
            '\'runas\' is being ignored in favor of \'user\'.'
        )
        runas = None
    elif runas is not None:
        # Support old runas usage
        user = runas
        runas = None

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = (
            'Service {0} is set to be stopped'.format(name))
    else:
        comment = 'Stopping service: {0}'.format(name)
        log.debug(comment)

        all_processes = __salt__['supervisord.status'](
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env
        )

        # parse process groups
        process_groups = []
        for proc in all_processes:
            if ':' in proc:
                process_groups.append(proc[:proc.index(':') + 1])
        process_groups = list(set(process_groups))

        is_stopped = None

        if name in process_groups:
            # check if any processes in this group are stopped
            is_stopped = False
            for proc in all_processes:
                if proc.startswith(name) \
                        and _is_stopped_state(all_processes[proc]['state']):
                    is_stopped = True
                    break

        elif name in all_processes:
            if _is_stopped_state(all_processes[name]['state']):
                is_stopped = True
            else:
                is_stopped = False
        else:
            # process name doesn't exist
            ret['comment'] = "Service {0} doesn't exist".format(name)

        if is_stopped is True:
            ret['comment'] = "Service {0} is not running".format(name)
        else:
            result = {name: __salt__['supervisord.stop'](
                name,
                user=user,
                conf_file=conf_file,
                bin_env=bin_env
            )}
            ret.update(_check_error(result, comment))
            log.debug(unicode(result))
    return ret