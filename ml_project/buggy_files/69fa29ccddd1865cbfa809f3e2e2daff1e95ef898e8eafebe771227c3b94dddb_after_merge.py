def map_config_to_obj(module):
    templatized_command = "%(ovs-vsctl)s -t %(timeout)s list %(table)s %(record)s"
    command = templatized_command % module.params
    rc, out, err = module.run_command(command, check_rc=True)
    if rc != 0:
        module.fail_json(msg=err)

    match = re.search(r'^' + module.params['col'] + r'(\s+):(\s+)(.*)$', out, re.M)

    col_value = match.group(3)

    # Map types require key argument
    has_key = module.params['key'] is not None
    is_map = MAP_RE.match(col_value)
    if is_map and not has_key:
        module.fail_json(
            msg="missing required arguments: key for map type of column")

    col_value_to_dict = {}
    if NON_EMPTY_MAP_RE.match(col_value):
        for kv in col_value[1:-1].split(', '):
            k, v = kv.split('=')
            col_value_to_dict[k.strip()] = v.strip()

    obj = {
        'table': module.params['table'],
        'record': module.params['record'],
        'col': module.params['col'],
    }

    if has_key and is_map:
        if module.params['key'] in col_value_to_dict:
            obj['key'] = module.params['key']
            obj['value'] = col_value_to_dict[module.params['key']]
    else:
            obj['value'] = str(col_value.strip())

    return obj