def fg(args, stdin=None):
    """
    xonsh command: fg

    Bring the currently active job to the foreground, or, if a single number is
    given as an argument, bring that job to the foreground. Additionally,
    specify "+" for the most recent job and "-" for the second most recent job.
    """
    _clear_dead_jobs()
    if len(tasks) == 0:
        return '', 'Cannot bring nonexistent job to foreground.\n'

    if len(args) == 0:
        act = tasks[0]  # take the last manipulated task by default
    elif len(args) == 1:
        try:
            if args[0] == '+':  # take the last manipulated task
                act = tasks[0]
            elif args[0] == '-':  # take the second to last manipulated task
                act = tasks[1]
            else:
                act = int(args[0])
        except (ValueError, IndexError):
            return '', 'Invalid job: {}\n'.format(args[0])

        if act not in builtins.__xonsh_all_jobs__:
            return '', 'Invalid job: {}\n'.format(args[0])
    else:
        return '', 'fg expects 0 or 1 arguments, not {}\n'.format(len(args))

    # Put this one on top of the queue
    tasks.remove(act)
    tasks.appendleft(act)

    job = get_task(act)
    job['bg'] = False
    job['status'] = "running"
    print_one_job(act)
    wait_for_active_job()