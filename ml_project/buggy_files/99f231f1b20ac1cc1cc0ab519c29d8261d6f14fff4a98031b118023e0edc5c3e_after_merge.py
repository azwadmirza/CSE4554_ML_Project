def get_value(arg, config, module):
    command = PARAM_TO_COMMAND_KEYMAP[arg]
    has_command = re.search(r'\s+{0}\s*$'.format(command), config, re.M)
    has_command_val = re.search(r'(?:{0}\s)(?P<value>.*)$'.format(command), config, re.M)

    if command == 'ip router ospf':
        value = ''
        if has_command_val:
            value_list = has_command_val.group('value').split()
            if arg == 'ospf':
                value = value_list[0]
            elif arg == 'area':
                value = value_list[2]
    elif command == 'ip ospf message-digest-key':
        value = ''
        if has_command_val:
            value_list = has_command_val.group('value').split()
            if arg == 'message_digest_key_id':
                value = value_list[0]
            elif arg == 'message_digest_algorithm_type':
                value = value_list[1]
            elif arg == 'message_digest_encryption_type':
                value = value_list[2]
                if value == '3':
                    value = '3des'
                elif value == '7':
                    value = 'cisco_type_7'
            elif arg == 'message_digest_password':
                value = value_list[3]
    elif arg == 'passive_interface':
        has_no_command = re.search(r'\s+no\s+{0}\s*$'.format(command), config, re.M)
        value = False
        if has_command and not has_no_command:
            value = True
    elif arg in BOOL_PARAMS:
        value = bool(has_command)
    else:
        value = ''
        if has_command_val:
            value = has_command_val.group('value')
    return value