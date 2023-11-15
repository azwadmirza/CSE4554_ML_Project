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
        xattrs = {'format': display}

        if '| display json' in command:
            xattrs['format'] = 'json'

        elif '| display xml' in command:
            xattrs['format'] = 'xml'

        items.append({'name': 'command', 'xattrs': xattrs, 'text': text})

    return items