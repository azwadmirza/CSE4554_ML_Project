def get_existing(module, args):
    existing = {}
    netcfg = CustomNetworkConfig(indent=2, contents=get_config(module))

    parents = ['vrf context {0}'.format(module.params['vrf'])]
    parents.append('address-family {0} {1}'.format(module.params['afi'],
                                            module.params['safi']))
    config = netcfg.get_section(parents)
    if config:
        splitted_config = config.splitlines()
        vrf_index = False
        for index in range(0, len(splitted_config) - 1):
            if 'vrf' in splitted_config[index].strip():
                vrf_index = index
                break
        if vrf_index:
            config = '\n'.join(splitted_config[0:vrf_index])

        for arg in args:
            if arg not in ['afi', 'safi', 'vrf']:
                existing[arg] = get_value(arg, config, module)

        existing['afi'] = module.params['afi']
        existing['safi'] = module.params['safi']
        existing['vrf'] = module.params['vrf']

    return existing