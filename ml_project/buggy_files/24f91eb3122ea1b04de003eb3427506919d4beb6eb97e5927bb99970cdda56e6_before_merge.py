def state_present(module, existing, proposed, candidate):
    commands = list()
    proposed_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, proposed)
    existing_commands = apply_key_map(PARAM_TO_COMMAND_KEYMAP, existing)

    for key, value in proposed_commands.items():
        if key == 'associate-vrf':
            command = 'member vni {0} {1}'.format(module.params['vni'], key)

            if value:
                commands.append(command)
            else:
                commands.append('no {0}'.format(command))

        elif key == 'peer-ip' and value != 'default':
            for peer in value:
                commands.append('{0} {1}'.format(key, peer))

        elif value is True:
            commands.append(key)

        elif value is False:
            commands.append('no {0}'.format(key))

        elif value == 'default':
            if existing_commands.get(key):
                existing_value = existing_commands.get(key)
                if key == 'peer-ip':
                    for peer in existing_value:
                        commands.append('no {0} {1}'.format(key, peer))
                else:
                    commands.append('no {0} {1}'.format(key, existing_value))
            else:
                if key.replace(' ', '_').replace('-', '_') in BOOL_PARAMS:
                    commands.append('no {0}'.format(key.lower()))
        else:
            command = '{0} {1}'.format(key, value.lower())
            commands.append(command)

    if commands:
        vni_command = 'member vni {0}'.format(module.params['vni'])
        ingress_replication_command = 'ingress-replication protocol static'
        interface_command = 'interface {0}'.format(module.params['interface'])

        if ingress_replication_command in commands:
            static_level_cmds = [cmd for cmd in commands if 'peer' in cmd]
            parents = [interface_command, vni_command, ingress_replication_command]
            candidate.add(static_level_cmds, parents=parents)
            commands = [cmd for cmd in commands if 'peer' not in cmd]

        if vni_command in commands:
            parents = [interface_command]
            commands.remove(vni_command)
            if module.params['assoc_vrf'] is None:
                parents.append(vni_command)
            candidate.add(commands, parents=parents)