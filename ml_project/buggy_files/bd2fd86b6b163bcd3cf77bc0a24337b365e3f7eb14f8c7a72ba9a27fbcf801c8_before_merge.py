def get_value(arg, config, module):
    custom = [
        'allowas_in_max',
        'additional_paths_send',
        'additional_paths_receive',
        'advertise_map_exist',
        'advertise_map_non_exist',
        'max_prefix_limit',
        'max_prefix_interval',
        'max_prefix_threshold',
        'max_prefix_warning',
        'next_hop_third_party',
        'soft_reconfiguration_in'
    ]
    command = PARAM_TO_COMMAND_KEYMAP[arg]
    has_command = re.search(r'\s+{0}\s*'.format(command), config, re.M)
    has_command_val = command_val_re.search(r'(?:{0}\s)(?P<value>.*)$'.format(command), config, re.M)

    if arg in custom:
        value = get_custom_value(arg, config, module)

    elif arg in BOOL_PARAMS:
        value = False
        if has_command:
            value = True

    elif command.split()[0] in ['filter-list', 'prefix-list', 'route-map']:
        value = ''
        direction = arg.rsplit('_', 1)[1]
        if has_command_val:
            params = has_command_val.group('value').split()
            if params[-1] == direction:
                value = params[0]

    elif arg == 'send_community':
        if has_command:
            value = 'none'
            if has_command_val:
                value = has_command_val.group('value')

    else:
        value = ''

        if has_command_val:
            value = has_command_val.group('value')

    return value