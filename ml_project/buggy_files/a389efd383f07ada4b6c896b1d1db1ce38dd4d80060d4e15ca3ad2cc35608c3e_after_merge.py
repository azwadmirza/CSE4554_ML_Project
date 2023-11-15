def get_interface_mode(interface, intf_type, module):
    command = 'show interface {0} | json'.format(interface)
    interface = {}
    mode = 'unknown'
    try:
        body = run_commands(module, [command])[0]
    except IndexError:
        return None

    if intf_type in ['ethernet', 'portchannel']:
        interface_table = body['TABLE_interface']['ROW_interface']
        mode = str(interface_table.get('eth_mode', 'layer3'))
        if mode == 'access' or mode == 'trunk':
            mode = 'layer2'
    elif intf_type == 'svi':
        mode = 'layer3'
    return mode