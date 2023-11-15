def build_vpn_connection_resource(cmd, name, location, tags, gateway1, gateway2, vpn_type, authorization_key,
                                  enable_bgp, routing_weight, shared_key, use_policy_based_traffic_selectors):
    vpn_properties = {
        'virtualNetworkGateway1': {'id': gateway1},
        'enableBgp': enable_bgp,
        'connectionType': vpn_type,
        'routingWeight': routing_weight
    }
    if authorization_key:
        vpn_properties['authorizationKey'] = "[parameters('authorizationKey')]"
    if cmd.supported_api_version(min_api='2017-03-01'):
        vpn_properties['usePolicyBasedTrafficSelectors'] = use_policy_based_traffic_selectors

    # add scenario specific properties
    if shared_key:
        shared_key = "[parameters('sharedKey')]"
    if vpn_type == 'IPSec':
        vpn_properties.update({
            'localNetworkGateway2': {'id': gateway2},
            'sharedKey': shared_key
        })
    elif vpn_type == 'Vnet2Vnet':
        vpn_properties.update({
            'virtualNetworkGateway2': {'id': gateway2},
            'sharedKey': shared_key
        })
    elif vpn_type == 'ExpressRoute':
        vpn_properties.update({
            'peer': {'id': gateway2}
        })

    vpn_connection = {
        'type': 'Microsoft.Network/connections',
        'name': name,
        'location': location,
        'tags': tags,
        'apiVersion': '2015-06-15',
        'dependsOn': [],
        'properties': vpn_properties if vpn_type != 'VpnClient' else {}
    }
    return vpn_connection