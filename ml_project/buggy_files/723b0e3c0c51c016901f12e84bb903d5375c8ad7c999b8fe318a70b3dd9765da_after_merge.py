def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        vrfs=dict(type='list'),

        name=dict(),
        description=dict(),
        rd=dict(),
        route_export=dict(type='list'),
        route_import=dict(type='list'),
        route_both=dict(type='list'),
        route_export_ipv4=dict(type='list'),
        route_import_ipv4=dict(type='list'),
        route_both_ipv4=dict(type='list'),
        route_export_ipv6=dict(type='list'),
        route_import_ipv6=dict(type='list'),
        route_both_ipv6=dict(type='list'),


        interfaces=dict(type='list'),
        associated_interfaces=dict(type='list'),

        delay=dict(default=10, type='int'),
        purge=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(ios_argument_spec)

    mutually_exclusive = [('name', 'vrfs')]
    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    result = {'changed': False}

    warnings = list()
    check_args(module, warnings)
    result['warnings'] = warnings

    want = map_params_to_obj(module)
    have = map_config_to_obj(module)
    commands = map_obj_to_commands(update_objects(want, have), module)

    if module.params['purge']:
        want_vrfs = [x['name'] for x in want]
        have_vrfs = [x['name'] for x in have]
        for item in set(have_vrfs).difference(want_vrfs):
            cmd = 'no vrf definition %s' % item
            if cmd not in commands:
                commands.append(cmd)

    result['commands'] = commands

    if commands:
        if not module.check_mode:
            load_config(module, commands)
        result['changed'] = True

    check_declarative_intent_params(want, module, result)

    module.exit_json(**result)