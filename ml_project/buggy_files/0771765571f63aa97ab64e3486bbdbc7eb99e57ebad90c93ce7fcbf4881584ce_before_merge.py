def main():
    argument_spec = dict(
        interface=dict(required=True, type='str'),
        ospf=dict(required=True, type='str'),
        area=dict(required=True, type='str'),
        cost=dict(required=False, type='str'),
        hello_interval=dict(required=False, type='str'),
        dead_interval=dict(required=False, type='str'),
        passive_interface=dict(required=False, type='bool'),
        message_digest=dict(required=False, type='bool'),
        message_digest_key_id=dict(required=False, type='str'),
        message_digest_algorithm_type=dict(required=False, type='str', choices=['md5']),
        message_digest_encryption_type=dict(required=False, type='str', choices=['cisco_type_7','3des']),
        message_digest_password=dict(required=False, type='str', no_log=True),
        state=dict(choices=['present', 'absent'], default='present', required=False),
        include_defaults=dict(default=True),
        config=dict(),
        save=dict(type='bool', default=False)
    )

    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                                required_together=[['message_digest_key_id',
                                                    'message_digest_algorithm_type',
                                                    'message_digest_encryption_type',
                                                    'message_digest_password']],
                                supports_check_mode=True)

    if not module.params['interface'].startswith('loopback'):
        module.params['interface'] = module.params['interface'].capitalize()

    warnings = list()
    check_args(module, warnings)

    for param in ['message_digest_encryption_type',
                  'message_digest_algorithm_type',
                  'message_digest_password']:
        if module.params[param] == 'default':
            module.exit_json(msg='Use message_digest_key_id=default to remove'
                                 ' an existing authentication configuration')

    state = module.params['state']
    args =  [
        'interface',
        'ospf',
        'area',
        'cost',
        'hello_interval',
        'dead_interval',
        'passive_interface',
        'message_digest',
        'message_digest_key_id',
        'message_digest_algorithm_type',
        'message_digest_encryption_type',
        'message_digest_password'
    ]

    existing = invoke('get_existing', module, args)
    end_state = existing
    proposed_args = dict((k, v) for k, v in module.params.items()
                    if v is not None and k in args)

    proposed = {}
    for key, value in proposed_args.items():
        if key != 'interface':
            if str(value).lower() == 'true':
                value = True
            elif str(value).lower() == 'false':
                value = False
            elif str(value).lower() == 'default':
                value = PARAM_TO_DEFAULT_KEYMAP.get(key)
                if value is None:
                    value = 'default'
            if existing.get(key) or (not existing.get(key) and value):
                proposed[key] = value

    proposed['area'] = normalize_area(proposed['area'], module)
    result = {}
    if (state == 'present' or (state == 'absent' and
            existing.get('ospf') == proposed['ospf'] and
            existing.get('area') == proposed['area'])):

        candidate = CustomNetworkConfig(indent=3)
        invoke('state_%s' % state, module, existing, proposed, candidate)
        response = load_config(module, candidate)
        result.update(response)

    else:
        result['updates'] = []

    if module._verbosity > 0:
        end_state = invoke('get_existing', module, args)
        result['end_state'] = end_state
        result['existing'] = existing
        result['proposed'] = proposed_args

    result['warnings'] = warnings

    module.exit_json(**result)