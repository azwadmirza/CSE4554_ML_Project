def run(module, result):
    match = module.params['match']
    replace = module.params['replace']
    path = module.params['parents']

    candidate = get_candidate(module)
    if match != 'none':
        contents = module.params['config']
        if not contents:
            contents = get_config(module)
        config = NetworkConfig(indent=1, contents=contents)
        configobjs = candidate.difference(config, path=path, match=match,
                                          replace=replace)

    else:
        configobjs = candidate.items

    total_commands = []
    if configobjs:
        commands = dumps(configobjs, 'commands').split('\n')

        if module.params['lines']:
            if module.params['before']:
                commands[:0] = module.params['before']

            if module.params['after']:
                commands.extend(module.params['after'])

        total_commands.extend(commands)
        result['updates'] = total_commands

    if module.params['save']:
            total_commands.append('configuration write')
    if total_commands:
        result['changed'] = True
        if not module.check_mode:
            load_config(module, total_commands)