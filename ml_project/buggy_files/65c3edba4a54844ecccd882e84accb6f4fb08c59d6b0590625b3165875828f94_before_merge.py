def main():
    argument_spec = dict(
        asn=dict(required=True, type='str'),
        vrf=dict(required=False, type='str', default='default'),
        neighbor=dict(required=True, type='str'),
        afi=dict(required=True, type='str'),
        safi=dict(required=True, type='str'),
        additional_paths_receive=dict(required=False, type='str', choices=['enable', 'disable', 'inherit']),
        additional_paths_send=dict(required=False, type='str', choices=['enable', 'disable', 'inherit']),
        advertise_map_exist=dict(required=False, type='list'),
        advertise_map_non_exist=dict(required=False, type='list'),
        allowas_in=dict(required=False, type='bool'),
        allowas_in_max=dict(required=False, type='str'),
        as_override=dict(required=False, type='bool'),
        default_originate=dict(required=False, type='bool'),
        default_originate_route_map=dict(required=False, type='str'),
        filter_list_in=dict(required=False, type='str'),
        filter_list_out=dict(required=False, type='str'),
        max_prefix_limit=dict(required=False, type='str'),
        max_prefix_interval=dict(required=False, type='str'),
        max_prefix_threshold=dict(required=False, type='str'),
        max_prefix_warning=dict(required=False, type='bool'),
        next_hop_self=dict(required=False, type='bool'),
        next_hop_third_party=dict(required=False, type='bool'),
        prefix_list_in=dict(required=False, type='str'),
        prefix_list_out=dict(required=False, type='str'),
        route_map_in=dict(required=False, type='str'),
        route_map_out=dict(required=False, type='str'),
        route_reflector_client=dict(required=False, type='bool'),
        send_community=dict(required=False, choices=['none', 'both', 'extended', 'standard', 'default']),
        soft_reconfiguration_in=dict(required=False, type='str', choices=['enable', 'always', 'inherit']),
        soo=dict(required=False, type='str'),
        suppress_inactive=dict(required=False, type='bool'),
        unsuppress_map=dict(required=False, type='str'),
        weight=dict(required=False, type='str'),
        state=dict(choices=['present', 'absent'], default='present', required=False),
    )
    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[['advertise_map_exist', 'advertise_map_non_exist']],
        required_together=[['max_prefix_limit', 'max_prefix_interval'],
                           ['max_prefix_limit', 'max_prefix_warning'],
                           ['max_prefix_limit', 'max_prefix_threshold']],
        supports_check_mode=True,
    )

    warnings = list()
    check_args(module, warnings)
    result = dict(changed=False, warnings=warnings)

    state = module.params['state']

    if module.params['vrf'] == 'default' and module.params['soo']:
        module.fail_json(msg='SOO is only allowed in non-default VRF')

    args = PARAM_TO_COMMAND_KEYMAP.keys()
    existing = get_existing(module, args, warnings)

    if existing.get('asn') and state == 'present':
        if existing.get('asn') != module.params['asn']:
            module.fail_json(msg='Another BGP ASN already exists.',
                             proposed_asn=module.params['asn'],
                             existing_asn=existing.get('asn'))

    for param in ['advertise_map_exist', 'advertise_map_non_exist']:
        if module.params[param] == ['default']:
            module.params[param] = 'default'

    proposed_args = dict((k, v) for k, v in module.params.items() if v is not None and k in args)

    proposed = {}
    for key, value in proposed_args.items():
        if key not in ['asn', 'vrf', 'neighbor']:
            if not isinstance(value, list):
                if str(value).lower() == 'true':
                    value = True
                elif str(value).lower() == 'false':
                    value = False
                elif str(value).lower() == 'default':
                    if key in BOOL_PARAMS:
                        value = False
                    else:
                        value = 'default'
            if existing.get(key) != value:
                proposed[key] = value

    candidate = CustomNetworkConfig(indent=3)
    if state == 'present':
        state_present(module, existing, proposed, candidate)
    elif state == 'absent' and existing:
        state_absent(module, existing, proposed, candidate)

    if candidate:
        candidate = candidate.items_text()
        load_config(module, candidate)
        result['changed'] = True
        result['commands'] = candidate
    else:
        result['commands'] = []

    module.exit_json(**result)