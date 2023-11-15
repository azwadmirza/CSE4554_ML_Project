def main():
    argument_spec = dict(
        asn=dict(required=True, type='str'),
        vrf=dict(required=False, type='str', default='default'),
        neighbor=dict(required=True, type='str'),
        description=dict(required=False, type='str'),
        capability_negotiation=dict(required=False, type='bool'),
        connected_check=dict(required=False, type='bool'),
        dynamic_capability=dict(required=False, type='bool'),
        ebgp_multihop=dict(required=False, type='str'),
        local_as=dict(required=False, type='str'),
        log_neighbor_changes=dict(required=False, type='str', choices=['enable', 'disable', 'inherit']),
        low_memory_exempt=dict(required=False, type='bool'),
        maximum_peers=dict(required=False, type='str'),
        pwd=dict(required=False, type='str'),
        pwd_type=dict(required=False, type='str', choices=['cleartext', '3des', 'cisco_type_7', 'default']),
        remote_as=dict(required=False, type='str'),
        remove_private_as=dict(required=False, type='str', choices=['enable', 'disable', 'all', 'replace-as']),
        shutdown=dict(required=False, type='bool'),
        suppress_4_byte_as=dict(required=False, type='bool'),
        timers_keepalive=dict(required=False, type='str'),
        timers_holdtime=dict(required=False, type='str'),
        transport_passive_only=dict(required=False, type='bool'),
        update_source=dict(required=False, type='str'),
        m_facts=dict(required=False, default=False, type='bool'),
        state=dict(choices=['present', 'absent'], default='present', required=False),
    )
    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=[['timers_holdtime', 'timers_keepalive']],
        supports_check_mode=True,
    )

    warnings = list()
    check_args(module, warnings)
    result = dict(changed=False, warnings=warnings)

    state = module.params['state']

    if module.params['pwd_type'] == 'default':
        module.params['pwd_type'] = '0'

    args = PARAM_TO_COMMAND_KEYMAP.keys()
    existing = get_existing(module, args, warnings)

    if existing.get('asn') and state == 'present':
        if existing['asn'] != module.params['asn']:
            module.fail_json(msg='Another BGP ASN already exists.',
                             proposed_asn=module.params['asn'],
                             existing_asn=existing.get('asn'))

    proposed_args = dict((k, v) for k, v in module.params.items()
                         if v is not None and k in args)
    proposed = {}
    for key, value in proposed_args.items():
        if key not in ['asn', 'vrf', 'neighbor', 'pwd_type']:
            if str(value).lower() == 'default':
                value = PARAM_TO_DEFAULT_KEYMAP.get(key, 'default')
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