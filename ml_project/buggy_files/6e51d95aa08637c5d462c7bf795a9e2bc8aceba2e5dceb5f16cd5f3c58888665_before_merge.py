def get_value(arg, config, module):
    custom = [
        'inject_map',
        'networks',
        'redistribute'
    ]

    if arg in custom:
        value = get_custom_list_value(config, arg, module)

    elif (arg.startswith('distance') or arg.startswith('dampening') or
          arg.startswith('table_map')):
        value = get_custom_string_value(config, arg, module)

    elif arg in BOOL_PARAMS:
        command_re = re.compile(r'\s+{0}\s*'.format(command), re.M)
        value = False

        if command_re.search(config):
            value = True

    else:
        command_val_re = re.compile(r'(?:{0}\s)(?P<value>.*)$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = ''

        has_command = command_val_re.search(config)
        if has_command:
            value = has_command.group('value')

    return value