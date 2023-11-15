def get_existing(module, args):
    existing = {}
    netcfg = get_config(module)
    parents = ['evpn', 'vni {0} l2'.format(module.params['vni'])]
    config = netcfg.get_section(parents)

    if config:
        for arg in args:
            if arg != 'vni':
                if arg == 'route_distinguisher':
                    existing[arg] = get_value(arg, config, module)
                else:
                    existing[arg] = get_route_target_value(arg, config, module)

        existing_fix = dict((k, v) for k, v in existing.items() if v)
        if existing_fix:
            existing['vni'] = module.params['vni']
        else:
            existing = existing_fix

    return existing