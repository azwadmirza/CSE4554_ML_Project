def get_interfaces_dict(module):
    """Gets all active interfaces on a given switch
    Returns:
        dictionary with interface type (ethernet,svi,loop,portchannel) as the
            keys.  Each value is a list of interfaces of given interface (key)
            type.
    """
    command = 'show interface status'
    try:
        body = execute_show_command(command, module)[0]
    except IndexError:
        body = {}

    interfaces = {
        'ethernet': [],
        'svi': [],
        'loopback': [],
        'management': [],
        'portchannel': [],
        'nve': [],
        'unknown': []
        }

    interface_list = body.get('TABLE_interface')['ROW_interface']
    for index in interface_list:
        intf = index['interface']
        intf_type = get_interface_type(intf)

        interfaces[intf_type].append(intf)

    return interfaces