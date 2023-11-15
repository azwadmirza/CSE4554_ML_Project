def parse_interfaces(module, vlan):
    vlan_int = []
    interfaces = vlan.get('vlanshowplist-ifidx')
    if interfaces:
        if isinstance(interfaces, list):
            interfaces_list = [i.strip() for i in interfaces]
            interfaces_str = ','.join(interfaces_list)
            vlan_int = get_vlan_int(interfaces_str)
        else:
            vlan_int = get_vlan_int(interfaces)
    return vlan_int