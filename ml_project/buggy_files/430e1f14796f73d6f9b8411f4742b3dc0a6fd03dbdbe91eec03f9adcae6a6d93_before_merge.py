def main():
    """entry point for module execution
    """
    argument_spec = dict(
        commands=dict(type='list'),
        rpcs=dict(type='list'),

        display=dict(choices=['text', 'json', 'xml'], aliases=['format', 'output']),

        wait_for=dict(type='list', aliases=['waitfor']),
        match=dict(default='all', choices=['all', 'any']),

        retries=dict(default=10, type='int'),
        interval=dict(default=1, type='int')
    )

    argument_spec.update(junos_argument_spec)

    required_one_of = [('commands', 'rpcs')]

    module = AnsibleModule(argument_spec=argument_spec,
                           required_one_of=required_one_of,
                           supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)

    items = list()
    items.extend(parse_commands(module, warnings))
    items.extend(parse_rpcs(module))

    wait_for = module.params['wait_for'] or list()
    conditionals = [Conditional(c) for c in wait_for]

    retries = module.params['retries']
    interval = module.params['interval']
    match = module.params['match']

    while retries > 0:
        responses = rpc(module, items)

        transformed = list()
        output = list()
        for item, resp in zip(items, responses):
            if item['xattrs']['format'] == 'xml':
                if not HAS_JXMLEASE:
                    module.fail_json(msg='jxmlease is required but does not appear to be installed. '
                                         'It can be installed using `pip install jxmlease`')

                try:
                    json_resp = jxmlease.parse(resp)
                    transformed.append(json_resp)
                    output.append(json_resp)
                except:
                    raise ValueError(resp)
            else:
                transformed.append(resp)

        for item in list(conditionals):
            try:
                if item(transformed):
                    if match == 'any':
                        conditionals = list()
                        break
                    conditionals.remove(item)
            except FailedConditionalError:
                pass

        if not conditionals:
            break

        time.sleep(interval)
        retries -= 1

    if conditionals:
        failed_conditions = [item.raw for item in conditionals]
        msg = 'One or more conditional statements have not be satisfied'
        module.fail_json(msg=msg, failed_conditions=failed_conditions)

    result = {
        'changed': False,
        'warnings': warnings,
        'stdout': responses,
        'stdout_lines': to_lines(responses)
    }

    if output:
        result['output'] = output

    module.exit_json(**result)