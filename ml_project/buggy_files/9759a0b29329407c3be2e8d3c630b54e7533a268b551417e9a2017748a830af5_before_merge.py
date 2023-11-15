def set_lb_outbound_rule(instance, cmd, parent, item_name, protocol=None, outbound_ports=None,
                         idle_timeout=None, frontend_ip_configurations=None, enable_tcp_reset=None,
                         backend_address_pool=None):
    SubResource = cmd.get_models('SubResource')
    _set_param(instance, 'protocol', protocol)
    _set_param(instance, 'allocated_outbound_ports', outbound_ports)
    _set_param(instance, 'idle_timeout_in_minutes', idle_timeout)
    _set_param(instance, 'enable_tcp_reset', enable_tcp_reset)
    _set_param(instance, 'backend_address_pool', SubResource(id=backend_address_pool)
               if backend_address_pool else None)
    _set_param(instance, 'frontend_ip_configurations',
               [SubResource(x) for x in frontend_ip_configurations] if frontend_ip_configurations else None)

    return parent