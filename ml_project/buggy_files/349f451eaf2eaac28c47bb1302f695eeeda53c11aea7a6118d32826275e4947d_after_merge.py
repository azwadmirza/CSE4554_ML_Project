def build_application_gateway_resource(cmd, name, location, tags, sku_name, sku_tier, capacity, servers, frontend_port,
                                       private_ip_address, private_ip_allocation, cert_data, cert_password,
                                       cookie_based_affinity, http_settings_protocol, http_settings_port,
                                       http_listener_protocol, routing_rule_type, public_ip_id, subnet_id,
                                       connection_draining_timeout, enable_http2):

    # set the default names
    frontend_ip_name = 'appGatewayFrontendIP'
    backend_pool_name = 'appGatewayBackendPool'
    frontend_port_name = 'appGatewayFrontendPort'
    http_listener_name = 'appGatewayHttpListener'
    http_settings_name = 'appGatewayBackendHttpSettings'
    routing_rule_name = 'rule1'
    ssl_cert_name = '{}SslCert'.format(name)

    ssl_cert = None

    frontend_ip_config = _build_frontend_ip_config(cmd, frontend_ip_name, public_ip_id, subnet_id,
                                                   private_ip_address, private_ip_allocation)
    backend_address_pool = {'name': backend_pool_name}
    if servers:
        backend_address_pool['properties'] = {'BackendAddresses': servers}

    def _ag_subresource_id(_type, name):
        return "[concat(variables('appGwID'), '/{}/{}')]".format(_type, name)

    frontend_ip_config_id = _ag_subresource_id('frontendIPConfigurations', frontend_ip_name)
    frontend_port_id = _ag_subresource_id('frontendPorts', frontend_port_name)
    http_listener_id = _ag_subresource_id('httpListeners', http_listener_name)
    backend_address_pool_id = _ag_subresource_id('backendAddressPools', backend_pool_name)
    backend_http_settings_id = _ag_subresource_id('backendHttpSettingsCollection',
                                                  http_settings_name)
    ssl_cert_id = _ag_subresource_id('sslCertificates', ssl_cert_name)

    http_listener = {
        'name': http_listener_name,
        'properties': {
            'FrontendIpConfiguration': {'Id': frontend_ip_config_id},
            'FrontendPort': {'Id': frontend_port_id},
            'Protocol': http_listener_protocol,
            'SslCertificate': None
        }
    }
    if cert_data:
        http_listener['properties'].update({'SslCertificate': {'id': ssl_cert_id}})
        ssl_cert = {
            'name': ssl_cert_name,
            'properties': {
                'data': cert_data,
            }
        }
        if cert_password:
            ssl_cert['properties']['password'] = "[parameters('certPassword')]"

    backend_http_settings = {
        'name': http_settings_name,
        'properties': {
            'Port': http_settings_port,
            'Protocol': http_settings_protocol,
            'CookieBasedAffinity': cookie_based_affinity
        }
    }
    if cmd.supported_api_version(min_api='2016-12-01'):
        backend_http_settings['properties']['connectionDraining'] = {
            'enabled': bool(connection_draining_timeout),
            'drainTimeoutInSec': connection_draining_timeout if connection_draining_timeout else 1
        }

    ag_properties = {
        'backendAddressPools': [backend_address_pool],
        'backendHttpSettingsCollection': [backend_http_settings],
        'frontendIPConfigurations': [frontend_ip_config],
        'frontendPorts': [
            {
                'name': frontend_port_name,
                'properties': {
                    'Port': frontend_port
                }
            }
        ],
        'gatewayIPConfigurations': [
            {
                'name': frontend_ip_name,
                'properties': {
                    'subnet': {'id': subnet_id}
                }
            }
        ],
        'httpListeners': [http_listener],
        'sku': {
            'name': sku_name,
            'tier': sku_tier,
            'capacity': capacity
        },
        'requestRoutingRules': [
            {
                'Name': routing_rule_name,
                'properties': {
                    'RuleType': routing_rule_type,
                    'httpListener': {'id': http_listener_id},
                    'backendAddressPool': {'id': backend_address_pool_id},
                    'backendHttpSettings': {'id': backend_http_settings_id}
                }
            }
        ]
    }
    if ssl_cert:
        ag_properties.update({'sslCertificates': [ssl_cert]})
    if enable_http2 and cmd.supported_api_version(min_api='2017-10-01'):
        ag_properties.update({'enableHttp2': enable_http2})

    ag = {
        'type': 'Microsoft.Network/applicationGateways',
        'name': name,
        'location': location,
        'tags': tags,
        'apiVersion': cmd.get_api_version(),
        'dependsOn': [],
        'properties': ag_properties
    }
    return ag