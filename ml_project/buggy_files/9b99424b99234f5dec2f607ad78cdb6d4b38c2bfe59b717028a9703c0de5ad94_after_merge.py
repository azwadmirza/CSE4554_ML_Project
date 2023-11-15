def run(module, result):
    match = module.params['match']
    replace = module.params['replace']
    replace_config = replace == 'config'
    path = module.params['parents']
    comment = module.params['comment']
    admin = module.params['admin']
    check_mode = module.check_mode

    candidate_config = get_candidate(module)
    running_config = get_running_config(module)

    sanitize_candidate_config(candidate_config.items)
    sanitize_running_config(running_config.items)

    commands = None
    if match != 'none' and replace != 'config':
        commands = candidate_config.difference(running_config, path=path, match=match, replace=replace)
    elif replace_config:
        can_config = candidate_config.difference(running_config, path=path, match=match, replace=replace)
        candidate = dumps(can_config, 'commands').split('\n')
        run_config = running_config.difference(candidate_config, path=path, match=match, replace=replace)
        running = dumps(run_config, 'commands').split('\n')

        if len(candidate) > 1 or len(running) > 1:
            ret = copy_file_to_node(module)
            if not ret:
                module.fail_json(msg='Copy of config file to the node failed')

            commands = ['load harddisk:/ansible_config.txt']
    else:
        commands = candidate_config.items

    if commands:
        if not replace_config:
            commands = dumps(commands, 'commands').split('\n')

        if any((module.params['lines'], module.params['src'])):
            if module.params['before']:
                commands[:0] = module.params['before']

            if module.params['after']:
                commands.extend(module.params['after'])

            result['commands'] = commands

        commit = not check_mode
        diff = load_config(module, commands, commit=commit, replace=replace_config, comment=comment, admin=admin)
        if diff:
            result['diff'] = dict(prepared=diff)

        result['changed'] = True