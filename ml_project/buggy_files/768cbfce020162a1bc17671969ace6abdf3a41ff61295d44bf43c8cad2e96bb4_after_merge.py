    def get_route_to(self, destination='', protocol=''):
        routes = {}

        # Placeholder for vrf arg
        vrf = ''

        # Right not iterating through vrfs is necessary
        # show ipv6 route doesn't support vrf 'all'
        if vrf == '':
            vrfs = sorted(self._get_vrfs())
        else:
            vrfs = [vrf]

        if protocol.lower() == 'direct':
            protocol = 'connected'

        try:
            ipv = ''
            if IPNetwork(destination).version == 6:
                ipv = 'v6'
        except AddrFormatError:
            return 'Please specify a valid destination!'

        commands = []
        for _vrf in vrfs:
            commands.append('show ip{ipv} route vrf {_vrf} {destination} {protocol} detail'.format(
                ipv=ipv,
                _vrf=_vrf,
                destination=destination,
                protocol=protocol,
            ))

        commands_output = self.device.run_commands(commands)

        for _vrf, command_output in zip(vrfs, commands_output):
            if ipv == 'v6':
                routes_out = command_output.get('routes', {})
            else:
                routes_out = command_output.get('vrfs', {}).get(_vrf, {}).get('routes', {})

            for prefix, route_details in routes_out.items():
                if prefix not in routes.keys():
                    routes[prefix] = []
                route_protocol = route_details.get('routeType')
                preference = route_details.get('preference', 0)

                route = {
                    'current_active': True,
                    'last_active': True,
                    'age': 0,
                    'next_hop': u'',
                    'protocol': route_protocol,
                    'outgoing_interface': u'',
                    'preference': preference,
                    'inactive_reason': u'',
                    'routing_table': _vrf,
                    'selected_next_hop': True,
                    'protocol_attributes': {}
                }
                if protocol == 'bgp' or route_protocol.lower() in ('ebgp', 'ibgp'):
                    nexthop_interface_map = {}
                    for next_hop in route_details.get('vias'):
                        nexthop_ip = napalm.base.helpers.ip(next_hop.get('nexthopAddr'))
                        nexthop_interface_map[nexthop_ip] = next_hop.get('interface')
                    metric = route_details.get('metric')
                    command = 'show ip{ipv} bgp {destination} detail vrf {_vrf}'.format(
                        ipv=ipv,
                        destination=prefix,
                        _vrf=_vrf
                    )
                    vrf_details = self.device.run_commands([command])[0].get(
                        'vrfs', {}).get(_vrf, {})
                    local_as = vrf_details.get('asn')
                    bgp_routes = vrf_details.get(
                        'bgpRouteEntries', {}).get(prefix, {}).get('bgpRoutePaths', [])
                    for bgp_route_details in bgp_routes:
                        bgp_route = route.copy()
                        as_path = bgp_route_details.get('asPathEntry', {}).get('asPath', u'')
                        remote_as = int(as_path.strip("()").split()[-1])
                        remote_address = napalm.base.helpers.ip(bgp_route_details.get(
                            'routeDetail', {}).get('peerEntry', {}).get('peerAddr', ''))
                        local_preference = bgp_route_details.get('localPreference')
                        next_hop = napalm.base.helpers.ip(bgp_route_details.get('nextHop'))
                        active_route = bgp_route_details.get('routeType', {}).get('active', False)
                        last_active = active_route  # should find smth better
                        communities = bgp_route_details.get('routeDetail', {}).get(
                            'communityList', [])
                        preference2 = bgp_route_details.get('weight')
                        inactive_reason = bgp_route_details.get('reasonNotBestpath', '')
                        bgp_route.update({
                            'current_active': active_route,
                            'inactive_reason': inactive_reason,
                            'last_active': last_active,
                            'next_hop': next_hop,
                            'outgoing_interface': nexthop_interface_map.get(next_hop),
                            'selected_next_hop': active_route,
                            'protocol_attributes': {
                                'metric': metric,
                                'as_path': as_path,
                                'local_preference': local_preference,
                                'local_as': local_as,
                                'remote_as': remote_as,
                                'remote_address': remote_address,
                                'preference2': preference2,
                                'communities': communities
                            }
                        })
                        routes[prefix].append(bgp_route)
                else:
                    if route_details.get('routeAction') in ('drop',):
                        route['next_hop'] = 'NULL'
                    if route_details.get('routingDisabled') is True:
                        route['last_active'] = False
                        route['current_active'] = False
                    for next_hop in route_details.get('vias'):
                        route_next_hop = route.copy()
                        if next_hop.get('nexthopAddr') is None:
                            route_next_hop.update(
                                {
                                    'next_hop': '',
                                    'outgoing_interface': next_hop.get('interface')
                                }
                            )
                        else:
                            route_next_hop.update(
                                {
                                    'next_hop': napalm.base.helpers.ip(next_hop.get('nexthopAddr')),
                                    'outgoing_interface': next_hop.get('interface')
                                }
                            )
                        routes[prefix].append(route_next_hop)
                    if route_details.get('vias') == []:  # empty list
                        routes[prefix].append(route)
        return routes