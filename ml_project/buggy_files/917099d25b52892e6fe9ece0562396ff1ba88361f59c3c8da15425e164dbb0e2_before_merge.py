def get_existing(module, args):
    existing = {}
    netcfg = get_config(module)

    interface_exist = check_interface(module, netcfg)
    if interface_exist:
        parents = ['interface port-channel{0}'.format(module.params['group'])]
        config = netcfg.get_section(parents)

        if config:
            existing['min_links'] = get_value('min_links', config, module)
            existing.update(get_portchannel(module, netcfg=netcfg))

    return existing, interface_exist