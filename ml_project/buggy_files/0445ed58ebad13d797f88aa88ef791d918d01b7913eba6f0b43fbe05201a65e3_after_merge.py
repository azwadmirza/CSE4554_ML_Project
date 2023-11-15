def get_existing(module, args):
    existing = {}
    netcfg = CustomNetworkConfig(indent=2, contents=get_config(module))

    interface_string = 'interface {0}'.format(module.params['interface'].lower())
    parents = [interface_string]
    config = netcfg.get_section(parents)

    if config:
        for arg in args:
            existing[arg] = get_value(arg, config, module)

        existing['interface'] = module.params['interface'].lower()
    else:
        if interface_string in str(netcfg):
            existing['interface'] = module.params['interface'].lower()
            for arg in args:
                existing[arg] = ''
    return existing