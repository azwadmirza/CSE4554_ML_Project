def main():
    argument_spec = dict(
        interface=dict(required=True, type='str'),
        vni=dict(required=True, type='str'),
        assoc_vrf=dict(required=False, type='bool'),
        multicast_group=dict(required=False, type='str'),
        peer_list=dict(required=False, type='list'),
        suppress_arp=dict(required=False, type='bool'),
        ingress_replication=dict(required=False, type='str',
                                     choices=['bgp', 'static', 'default']),
        state=dict(choices=['present', 'absent'], default='present',
                       required=False),
        include_defaults=dict(default=True),
        config=dict(),
        save=dict(type='bool', default=False)
    )

    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                                supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)


    if module.params['assoc_vrf']:
        mutually_exclusive_params = ['multicast_group',
                                     'suppress_arp',
                                     'ingress_replication']
        for param in mutually_exclusive_params:
            if module.params[param]:
                module.fail_json(msg='assoc_vrf cannot be used with '
                                     '{0} param'.format(param))
    if module.params['peer_list']:
        if module.params['ingress_replication'] != 'static':
            module.fail_json(msg='ingress_replication=static is required '
                                 'when using peer_list param')
        else:
            peer_list = module.params['peer_list']
            if peer_list[0] == 'default':
                module.params['peer_list'] = 'default'
            else:
                stripped_peer_list = map(str.strip, peer_list)
                module.params['peer_list'] = stripped_peer_list

    state = module.params['state']
    args =  [
        'assoc_vrf',
        'interface',
        'vni',
        'ingress_replication',
        'multicast_group',
        'peer_list',
        'suppress_arp'
    ]

    existing, interface_exist = invoke('get_existing', module, args)
    end_state = existing
    proposed_args = dict((k, v) for k, v in module.params.items()
                    if v is not None and k in args)

    proposed = {}
    for key, value in proposed_args.items():
        if key != 'interface':
            if str(value).lower() == 'default':
                value = PARAM_TO_DEFAULT_KEYMAP.get(key)
                if value is None:
                    value = 'default'
            if existing.get(key) or (not existing.get(key) and value):
                proposed[key] = value

    result = {}
    if state == 'present' or (state == 'absent' and existing):
        if not interface_exist:
            WARNINGS.append("The proposed NVE interface does not exist. "
                            "Use nxos_interface to create it first.")
        elif interface_exist != module.params['interface']:
            module.fail_json(msg='Only 1 NVE interface is allowed on '
                                 'the switch.')
        elif (existing and state == 'absent' and
                existing['vni'] != module.params['vni']):
            module.fail_json(msg="ERROR: VNI delete failed: Could not find"
                                 " vni node for {0}".format(
                                     module.params['vni']),
                                 existing_vni=existing['vni'])
        else:
            candidate = CustomNetworkConfig(indent=3)
            invoke('state_%s' % state, module, existing, proposed, candidate)

            try:
                response = load_config(module, candidate)
                result.update(response)
            except ShellError:
                exc = get_exception()
                module.fail_json(msg=str(exc))
    else:
        result['updates'] = []

    if module._verbosity > 0:
        end_state, interface_exist = invoke('get_existing', module, args)
        result['end_state'] = end_state
        result['existing'] = existing
        result['proposed'] = proposed_args

    if WARNINGS:
        result['warnings'] = WARNINGS

    module.exit_json(**result)