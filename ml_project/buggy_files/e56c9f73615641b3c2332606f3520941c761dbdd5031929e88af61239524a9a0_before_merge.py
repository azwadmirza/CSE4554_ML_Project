def get_vm_details(resource_group_name, vm_name):
    result = get_instance_view(resource_group_name, vm_name)
    network_client = get_mgmt_service_client(ResourceType.MGMT_NETWORK)
    public_ips = []
    fqdns = []
    private_ips = []
    mac_addresses = []
    # pylint: disable=line-too-long,no-member
    for nic_ref in result.network_profile.network_interfaces:
        nic_parts = parse_resource_id(nic_ref.id)
        nic = network_client.network_interfaces.get(nic_parts['resource_group'], nic_parts['name'])
        if nic.mac_address:
            mac_addresses.append(nic.mac_address)
        for ip_configuration in nic.ip_configurations:
            private_ips.append(ip_configuration.private_ip_address)
            if ip_configuration.public_ip_address:
                res = parse_resource_id(ip_configuration.public_ip_address.id)
                public_ip_info = network_client.public_ip_addresses.get(res['resource_group'],
                                                                        res['name'])
                if public_ip_info.ip_address:
                    public_ips.append(public_ip_info.ip_address)
                if public_ip_info.dns_settings:
                    fqdns.append(public_ip_info.dns_settings.fqdn)

    setattr(result, 'power_state',
            ','.join([s.display_status for s in result.instance_view.statuses if s.code.startswith('PowerState/')]))
    setattr(result, 'public_ips', ','.join(public_ips))
    setattr(result, 'fqdns', ','.join(fqdns))
    setattr(result, 'private_ips', ','.join(private_ips))
    setattr(result, 'mac_addresses', ','.join(mac_addresses))
    del result.instance_view  # we don't need other instance_view info as people won't care
    return result