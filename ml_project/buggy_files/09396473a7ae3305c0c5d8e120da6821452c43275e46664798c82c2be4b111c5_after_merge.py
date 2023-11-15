def get_portchannel_mode(interface, protocol, module, netcfg):
    if protocol != 'LACP':
        mode = 'on'
    else:
        netcfg = CustomNetworkConfig(indent=2, contents=get_config(module))
        parents = ['interface {0}'.format(interface.capitalize())]
        body = netcfg.get_section(parents)

        mode_list = body.split('\n')

        for line in mode_list:
            this_line = line.strip()
            if this_line.startswith('channel-group'):
                find = this_line
        if 'mode' in find:
            if 'passive' in find:
                mode = 'passive'
            elif 'active' in find:
                mode = 'active'

    return mode