def get_interface_info_dot_net():
    '''
    Uses .NET 4.0+ to gather Network Interface information. Should only run on
    Windows systems newer than Windows 7/Server 2008R2

    Returns:
        dict: A dictionary of information about all interfaces on the system
    '''
    interfaces = _get_network_interfaces()

    int_dict = {}
    for i_face in interfaces:
        int_dict[i_face.Name] = _get_base_properties(i_face)
        int_dict[i_face.Name].update(_get_ip_base_properties(i_face))
        int_dict[i_face.Name].update(_get_ip_unicast_info(i_face))
        int_dict[i_face.Name].update(_get_ip_gateway_info(i_face))
        int_dict[i_face.Name].update(_get_ip_dns_info(i_face))
        int_dict[i_face.Name].update(_get_ip_multicast_info(i_face))
        int_dict[i_face.Name].update(_get_ip_anycast_info(i_face))
        int_dict[i_face.Name].update(_get_ip_wins_info(i_face))

    return int_dict