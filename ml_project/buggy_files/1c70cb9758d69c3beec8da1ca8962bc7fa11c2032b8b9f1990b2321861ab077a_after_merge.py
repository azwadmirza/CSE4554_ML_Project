def main():
    argument_spec = dict(
        asn=dict(required=True, type='str'),
        vrf=dict(required=False, type='str', default='default'),
        safi=dict(required=True, type='str', choices=['unicast', 'multicast', 'evpn']),
        afi=dict(required=True, type='str', choices=['ipv4', 'ipv6', 'vpnv4', 'vpnv6', 'l2vpn']),
        additional_paths_install=dict(required=False, type='bool'),
        additional_paths_receive=dict(required=False, type='bool'),
        additional_paths_selection=dict(required=False, type='str'),
        additional_paths_send=dict(required=False, type='bool'),
        advertise_l2vpn_evpn=dict(required=False, type='bool'),
        client_to_client=dict(required=False, type='bool'),
        dampen_igp_metric=dict(required=False, type='str'),
        dampening_state=dict(required=False, type='bool'),
        dampening_half_time=dict(required=False, type='str'),
        dampening_max_suppress_time=dict(required=False, type='str'),
        dampening_reuse_time=dict(required=False, type='str'),
        dampening_routemap=dict(required=False, type='str'),
        dampening_suppress_time=dict(required=False, type='str'),
        default_information_originate=dict(required=False, type='bool'),
        default_metric=dict(required=False, type='str'),
        distance_ebgp=dict(required=False, type='str'),
        distance_ibgp=dict(required=False, type='str'),
        distance_local=dict(required=False, type='str'),
        inject_map=dict(required=False, type='list'),
        maximum_paths=dict(required=False, type='str'),
        maximum_paths_ibgp=dict(required=False, type='str'),
        networks=dict(required=False, type='list'),
        next_hop_route_map=dict(required=False, type='str'),
        redistribute=dict(required=False, type='list'),
        suppress_inactive=dict(required=False, type='bool'),
        table_map=dict(required=False, type='str'),
        table_map_filter=dict(required=False, type='bool'),
        state=dict(choices=['present', 'absent'], default='present', required=False),
    )

    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=[DAMPENING_PARAMS, ['distance_ibgp', 'distance_ebgp', 'distance_local']],
        supports_check_mode=True,
    )

    warnings = list()
    check_args(module, warnings)
    result = dict(changed=False, warnings=warnings)

    state = module.params['state']

    if module.params['dampening_routemap']:
        for param in DAMPENING_PARAMS:
            if module.params[param]:
                module.fail_json(msg='dampening_routemap cannot be used with'
                                     ' the {0} param'.format(param))

    if module.params['advertise_l2vpn_evpn']:
        if module.params['vrf'] == 'default':
            module.fail_json(msg='It is not possible to advertise L2VPN '
                                 'EVPN in the default VRF. Please specify '
                                 'another one.', vrf=module.params['vrf'])

    if module.params['table_map_filter'] and not module.params['table_map']:
        module.fail_json(msg='table_map param is needed when using'
                             ' table_map_filter filter.')

    args = PARAM_TO_COMMAND_KEYMAP.keys()
    existing = get_existing(module, args, warnings)

    if existing.get('asn') and state == 'present':
        if existing.get('asn') != module.params['asn']:
            module.fail_json(msg='Another BGP ASN already exists.',
                             proposed_asn=module.params['asn'],
                             existing_asn=existing.get('asn'))

    proposed_args = dict((k, v) for k, v in module.params.items()
                         if v is not None and k in args)

    for arg in ['networks', 'inject_map']:
        if proposed_args.get(arg):
            if proposed_args[arg][0] == 'default':
                proposed_args[arg] = 'default'

    proposed = {}
    for key, value in proposed_args.items():
        if key not in ['asn', 'vrf']:
            if str(value).lower() == 'default':
                value = PARAM_TO_DEFAULT_KEYMAP.get(key, 'default')
            if existing.get(key) != value:
                proposed[key] = value

    candidate = CustomNetworkConfig(indent=3)
    if state == 'present':
        state_present(module, existing, proposed, candidate)
    elif state == 'absent' and existing:
        state_absent(module, candidate)

    if candidate:
        candidate = candidate.items_text()
        load_config(module, candidate)
        result['changed'] = True
        result['commands'] = candidate
    else:
        result['commands'] = []

    module.exit_json(**result)