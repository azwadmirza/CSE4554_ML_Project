def parse_commands(module, warnings):
    items = list()

    for command in (module.params['commands'] or list()):
        if module.check_mode and not command.startswith('show'):
            warnings.append(
                'Only show commands are supported when using check_mode, not '
                'executing %s' % command
            )

        parts = command.split('|')
        text = parts[0]

        display = module.params['display'] or 'text'

        if '| display json' in command:
            display = 'json'

        elif '| display xml' in command:
            display = 'xml'

        if display == 'set' or '| display set' in command:
            if command.startswith('show configuration'):
                display = 'set'
            else:
                module.fail_json(msg="Invalid display option '%s' given for command '%s'" % ('set', command))

        xattrs = {'format': display}
        items.append({'name': 'command', 'xattrs': xattrs, 'text': text})

    return items