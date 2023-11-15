def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        src=dict(type='path'),

        lines=dict(aliases=['commands'], type='list'),
        parents=dict(type='list'),

        before=dict(type='list'),
        after=dict(type='list'),

        match=dict(default='line', choices=['line', 'strict', 'exact', 'none']),
        replace=dict(default='line', choices=['line', 'block']),
        multiline_delimiter=dict(default='@'),

        # this argument is deprecated (2.2) in favor of setting match: none
        # it will be removed in a future version
        force=dict(default=False, type='bool'),

        config=dict(),
        defaults=dict(type='bool', default=False),

        backup=dict(type='bool', default=False),
        save=dict(type='bool', default=False),
    )

    argument_spec.update(ios_argument_spec)

    mutually_exclusive = [('lines', 'src')]

    required_if = [('match', 'strict', ['lines']),
                   ('match', 'exact', ['lines']),
                   ('replace', 'block', ['lines'])]

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           required_if=required_if,
                           supports_check_mode=True)

    if module.params['force'] is True:
        module.params['match'] = 'none'

    result = {'changed': False}

    warnings = list()
    check_args(module, warnings)
    result['warnings'] = warnings

    if any((module.params['lines'], module.params['src'])):
        match = module.params['match']
        replace = module.params['replace']
        path = module.params['parents']

        candidate, want_banners = get_candidate(module)

        if match != 'none':
            config, have_banners = get_running_config(module)
            path = module.params['parents']
            configobjs = candidate.difference(config, path=path, match=match,
                                              replace=replace)
        else:
            configobjs = candidate.items
            have_banners = {}

        banners = diff_banners(want_banners, have_banners)

        if configobjs or banners:
            commands = dumps(configobjs, 'commands').split('\n')

            if module.params['lines']:
                if module.params['before']:
                    commands[:0] = module.params['before']

                if module.params['after']:
                    commands.extend(module.params['after'])

            result['commands'] = commands
            result['banners'] = banners

            # send the configuration commands to the device and merge
            # them with the current running config
            if not module.check_mode:
                if commands:
                    load_config(module, commands)
                if banners:
                    load_banners(module, banners)

            result['changed'] = True

    if module.params['backup']:
        result['__backup__'] = get_config(module=module)

    if module.params['save']:
        if not module.check_mode:
            run_commands(module, ['copy running-config startup-config\r'])
        result['changed'] = True

    module.exit_json(**result)