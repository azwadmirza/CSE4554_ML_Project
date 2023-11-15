def main():
    argument_spec = dict(
        server_type=dict(type='str', choices=['radius', 'tacacs'], required=True),
        global_key=dict(type='str'),
        encrypt_type=dict(type='str', choices=['0', '7']),
        deadtime=dict(type='str'),
        server_timeout=dict(type='str'),
        directed_request=dict(type='str', choices=['enabled', 'disabled', 'default']),
        state=dict(choices=['default', 'present'], default='present'),
    )

    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)
    results = {'changed': False, 'commands': [], 'warnings': warnings}

    server_type = module.params['server_type']
    global_key = module.params['global_key']
    encrypt_type = module.params['encrypt_type']
    deadtime = module.params['deadtime']
    server_timeout = module.params['server_timeout']
    directed_request = module.params['directed_request']
    state = module.params['state']

    if encrypt_type and not global_key:
        module.fail_json(msg='encrypt_type must be used with global_key.')

    args = dict(server_type=server_type, global_key=global_key,
                encrypt_type=encrypt_type, deadtime=deadtime,
                server_timeout=server_timeout, directed_request=directed_request)

    proposed = dict((k, v) for k, v in args.items() if v is not None)

    existing = get_aaa_server_info(server_type, module)

    commands = []
    if state == 'present':
        if deadtime:
            try:
                if int(deadtime) < 0 or int(deadtime) > 1440:
                    raise ValueError
            except ValueError:
                module.fail_json(
                    msg='deadtime must be an integer between 0 and 1440')

        if server_timeout:
            try:
                if int(server_timeout) < 1 or int(server_timeout) > 60:
                    raise ValueError
            except ValueError:
                module.fail_json(
                    msg='server_timeout must be an integer between 1 and 60')

        delta = dict(set(proposed.items()).difference(
            existing.items()))
        if delta:
            command = config_aaa_server(delta, server_type)
            if command:
                commands.append(command)

    elif state == 'default':
        for key, value in proposed.items():
            if key != 'server_type' and value != 'default':
                module.fail_json(
                    msg='Parameters must be set to "default"'
                        'when state=default')
        command = default_aaa_server(existing, proposed, server_type)
        if command:
            commands.append(command)

    cmds = flatten_list(commands)
    if cmds:
        results['changed'] = True
        if not module.check_mode:
            load_config(module, cmds)
        if 'configure' in cmds:
            cmds.pop(0)
        results['commands'] = cmds

    module.exit_json(**results)