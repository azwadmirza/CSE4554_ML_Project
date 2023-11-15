def map_obj_to_commands(updates, module):
    commands = list()

    for update in updates:
        want, have = update

        def needs_update(want, have, x):
            if isinstance(want.get(x), list) and isinstance(have.get(x), list):
                return want.get(x) and (want.get(x) != have.get(x)) and not all(elem in have.get(x) for elem in want.get(x))
            return want.get(x) and (want.get(x) != have.get(x))

        if want['state'] == 'absent':
            commands.append('no vrf definition %s' % want['name'])
            continue

        if not have.get('state'):
            commands.extend([
                'vrf definition %s' % want['name'],
                'address-family ipv4', 'exit',
                'address-family ipv6', 'exit',
            ])

        if needs_update(want, have, 'description'):
            cmd = 'description %s' % want['description']
            add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'rd'):
            cmd = 'rd %s' % want['rd']
            add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'route_import'):
            for route in want['route_import']:
                cmd = 'route-target import %s' % route
                add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'route_export'):
            for route in want['route_export']:
                cmd = 'route-target export %s' % route
                add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'route_import_ipv4'):
                cmd = 'address-family ipv4'
                add_command_to_vrf(want['name'], cmd, commands)
                for route in want['route_import_ipv4']:
                    cmd = 'route-target import %s' % route
                    add_command_to_vrf(want['name'], cmd, commands)
                cmd = 'exit-address-family'
                add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'route_export_ipv4'):
                cmd = 'address-family ipv4'
                add_command_to_vrf(want['name'], cmd, commands)
                for route in want['route_export_ipv4']:
                    cmd = 'route-target export %s' % route
                    add_command_to_vrf(want['name'], cmd, commands)
                cmd = 'exit-address-family'
                add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'route_import_ipv6'):
                cmd = 'address-family ipv6'
                add_command_to_vrf(want['name'], cmd, commands)
                for route in want['route_import_ipv6']:
                    cmd = 'route-target import %s' % route
                    add_command_to_vrf(want['name'], cmd, commands)
                cmd = 'exit-address-family'
                add_command_to_vrf(want['name'], cmd, commands)

        if needs_update(want, have, 'route_export_ipv6'):
                cmd = 'address-family ipv6'
                add_command_to_vrf(want['name'], cmd, commands)
                for route in want['route_export_ipv6']:
                    cmd = 'route-target export %s' % route
                    add_command_to_vrf(want['name'], cmd, commands)
                cmd = 'exit-address-family'
                add_command_to_vrf(want['name'], cmd, commands)

        if want['interfaces'] is not None:
            # handle the deletes
            for intf in set(have.get('interfaces', [])).difference(want['interfaces']):
                commands.extend(['interface %s' % intf,
                                 'no vrf forwarding %s' % want['name']])

            # handle the adds
            for intf in set(want['interfaces']).difference(have.get('interfaces', [])):
                cfg = get_config(module)
                configobj = NetworkConfig(indent=1, contents=cfg)
                children = configobj['interface %s' % intf].children
                intf_config = '\n'.join(children)

                commands.extend(['interface %s' % intf,
                                 'vrf forwarding %s' % want['name']])

                match = re.search('ip address .+', intf_config, re.M)
                if match:
                    commands.append(match.group())

    return commands