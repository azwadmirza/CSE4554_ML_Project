def add_lb_backend_address_pool_address(cmd, resource_group_name, load_balancer_name, backend_address_pool_name,
                                        address_name, vnet, ip_address):
    client = network_client_factory(cmd.cli_ctx).load_balancer_backend_address_pools
    address_pool = client.get(resource_group_name, load_balancer_name, backend_address_pool_name)
    (LoadBalancerBackendAddress,
     VirtualNetwork) = cmd.get_models('LoadBalancerBackendAddress',
                                      'VirtualNetwork')
    new_address = LoadBalancerBackendAddress(name=address_name,
                                             virtual_network=VirtualNetwork(id=vnet) if vnet else None,
                                             ip_address=ip_address if ip_address else None)
    address_pool.load_balancer_backend_addresses.append(new_address)
    return client.create_or_update(resource_group_name, load_balancer_name, backend_address_pool_name, address_pool)