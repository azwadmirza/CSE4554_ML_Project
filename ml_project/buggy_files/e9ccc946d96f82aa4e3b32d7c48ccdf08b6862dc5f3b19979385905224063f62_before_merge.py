def map_config_to_obj(module):
    config = get_config(module)
    configobj = NetworkConfig(indent=1, contents=config)
    match = re.findall(r'^vrf definition (\S+)', config, re.M)
    if not match:
        return list()

    instances = list()

    for item in set(match):
        obj = {
            'name': item,
            'state': 'present',
            'description': parse_description(configobj, item),
            'rd': parse_rd(configobj, item),
            'interfaces': parse_interfaces(configobj, item),
            'route_import': parse_import(configobj, item),
            'route_export': parse_export(configobj, item),
            'route_both': parse_both(configobj, item)
        }
        instances.append(obj)
    return instances