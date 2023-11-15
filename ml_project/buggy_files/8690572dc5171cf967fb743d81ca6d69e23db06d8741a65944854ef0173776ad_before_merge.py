def parse_commands(module, warnings):
    spec = dict(
        command=dict(key=True),
        output=dict(default=module.params['display'], choices=['text', 'json']),
        prompt=dict(),
        response=dict()
    )

    transform = ComplexList(spec, module)
    commands = transform(module.params['commands'])

    for index, item in enumerate(commands):
        if module.check_mode and not item['command'].startswith('show'):
            warnings.append(
                'Only show commands are supported when using check_mode, not '
                'executing %s' % item['command']
            )

        if item['output'] == 'json' and 'display json' not in item['command']:
            item['command'] += '| display json'
        elif item['output'] == 'text' and 'display json' in item['command']:
            item['command'] = item['command'].replace('| display json', '')

        commands[index] = item

    return commands