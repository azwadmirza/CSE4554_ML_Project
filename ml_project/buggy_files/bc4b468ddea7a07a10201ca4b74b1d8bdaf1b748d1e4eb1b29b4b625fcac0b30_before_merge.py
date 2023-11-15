def ensure_subnet_present(conn, module):
    subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])
    changed = False
    if subnet is None:
        if not module.check_mode:
            subnet = create_subnet(conn, module, module.params['vpc_id'], module.params['cidr'], ipv6_cidr=module.params['ipv6_cidr'], az=module.params['az'])
        changed = True
        # Subnet will be None when check_mode is true
        if subnet is None:
            return {
                'changed': changed,
                'subnet': {}
            }

    if module.params['ipv6_cidr'] != subnet.get('ipv6_cidr_block'):
        if ensure_ipv6_cidr_block(conn, module, subnet, module.params['ipv6_cidr'], module.check_mode):
            changed = True

    if module.params['map_public'] != subnet['map_public_ip_on_launch']:
        ensure_map_public(conn, module, subnet, module.params['map_public'], module.check_mode)
        changed = True

    if module.params['assign_instances_ipv6'] != subnet.get('assign_ipv6_address_on_creation'):
        ensure_assign_ipv6_on_create(conn, module, subnet, module.params['assign_instances_ipv6'], module.check_mode)
        changed = True

    if module.params['tags'] != subnet['tags']:
        if ensure_tags(conn, module, subnet, module.params['tags'], module.params['purge_tags']):
            changed = True

    subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])

    return {
        'changed': changed,
        'subnet': subnet
    }