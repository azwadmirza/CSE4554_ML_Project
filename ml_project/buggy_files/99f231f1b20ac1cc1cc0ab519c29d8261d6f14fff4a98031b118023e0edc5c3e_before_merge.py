def get_value(arg, config, module):
    custom = [
        'ospf',
        'area',
        'message_digest_key_id',
        'message_digest_algorithm_type',
        'message_digest_encryption_type',
        'message_digest_password',
        'passive_interface'
    ]

    if arg in custom:
        value = get_custom_value(arg, config, module)
    elif arg in BOOL_PARAMS:
        REGEX = re.compile(r'\s+{0}\s*$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = False
        try:
            if REGEX.search(config):
                value = True
        except TypeError:
            value = False
    else:
        REGEX = re.compile(r'(?:{0}\s)(?P<value>.*)$'.format(PARAM_TO_COMMAND_KEYMAP[arg]), re.M)
        value = ''
        if PARAM_TO_COMMAND_KEYMAP[arg] in config:
            value = REGEX.search(config).group('value')
    return value