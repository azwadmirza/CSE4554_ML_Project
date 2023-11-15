def get_existing(module, prefix, warnings):
    key_map = ['tag', 'pref', 'route_name', 'next_hop']
    netcfg = CustomNetworkConfig(indent=2, contents=get_config(module))
    parents = 'vrf context {0}'.format(module.params['vrf'])
    prefix_to_regex = fix_prefix_to_regex(prefix)

    route_regex = ('.*ip\sroute\s{0}\s(?P<next_hop>\S+)(\sname\s(?P<route_name>\S+))?'
                   '(\stag\s(?P<tag>\d+))?(\s(?P<pref>\d+)).*'.format(prefix_to_regex))

    if module.params['vrf'] == 'default':
        config = str(netcfg)
    else:
        config = netcfg.get_section(parents)

    if config:
        try:
            match_route = re.match(route_regex, config, re.DOTALL)
            group_route = match_route.groupdict()

            for key in key_map:
                if key not in group_route:
                    group_route[key] = ''
            group_route['prefix'] = prefix
            group_route['vrf'] = module.params['vrf']
        except (AttributeError, TypeError):
            group_route = {}
    else:
        group_route = {}
        msg = ("VRF {0} didn't exist.".format(module.params['vrf']))
        if msg not in warnings:
            warnings.append(msg)

    return group_route