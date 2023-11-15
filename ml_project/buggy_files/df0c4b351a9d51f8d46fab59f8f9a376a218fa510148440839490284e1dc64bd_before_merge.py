def list_(show_all=False, return_yaml=True):
    '''
    List the jobs currently scheduled on the minion

    CLI Example:

    .. code-block:: bash

        salt '*' schedule.list

        salt '*' schedule.list show_all=True
    '''

    schedule = __opts__['schedule'].copy()
    if 'schedule' in __pillar__:
        schedule.update(__pillar__['schedule'])

    for job in schedule.keys():  # iterate over a copy since we will mutate it
        if job == 'enabled':
            continue

        # Default jobs added by salt begin with __
        # by default hide them unless show_all is True.
        if job.startswith('__') and not show_all:
            del schedule[job]
            continue

        for item in schedule[job]:
            if item not in SCHEDULE_CONF:
                del schedule[job][item]
                continue
            if schedule[job][item] == 'true':
                schedule[job][item] = True
            if schedule[job][item] == 'false':
                schedule[job][item] = False

        if '_seconds' in schedule[job]:
            schedule[job]['seconds'] = schedule[job]['_seconds']
            del schedule[job]['_seconds']

    if schedule:
        if return_yaml:
            tmp = {'schedule': schedule}
            yaml_out = yaml.safe_dump(tmp, default_flow_style=False)
            return yaml_out
        else:
            return schedule
    else:
        return {'schedule': {}}