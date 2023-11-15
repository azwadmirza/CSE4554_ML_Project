def main():

    argument_spec = dict(
        interface=dict(required=False,),
        admin_state=dict(default='up', choices=['up', 'down'], required=False),
        description=dict(required=False, default=None),
        mode=dict(choices=['layer2', 'layer3'], required=False),
        interface_type=dict(required=False, choices=['loopback', 'portchannel', 'svi', 'nve']),
        ip_forward=dict(required=False, choices=['enable', 'disable']),
        fabric_forwarding_anycast_gateway=dict(required=False, type='bool'),
        state=dict(choices=['absent', 'present', 'default'], default='present', required=False)
    )

    argument_spec.update(nxos_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=[['interface', 'interface_type']],
                           supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)

    results = dict(changed=False, warnings=warnings)

    interface = module.params['interface']
    interface_type = module.params['interface_type']
    admin_state = module.params['admin_state']
    description = module.params['description']
    mode = module.params['mode']
    ip_forward = module.params['ip_forward']
    fabric_forwarding_anycast_gateway = module.params['fabric_forwarding_anycast_gateway']
    state = module.params['state']

    if interface:
        interface = interface.lower()
        intf_type = get_interface_type(interface)
        normalized_interface = normalize_interface(interface)

        if normalized_interface == 'Vlan1' and state == 'absent':
            module.fail_json(msg='ERROR: CANNOT REMOVE VLAN 1!')

        if intf_type == 'nve':
            if description or mode:
                module.fail_json(msg='description and mode params are not '
                                     'supported in this module. Use '
                                     'nxos_vxlan_vtep instead.')
        if (ip_forward or fabric_forwarding_anycast_gateway) and intf_type != 'svi':
            module.fail_json(msg='The ip_forward and '
                                 'fabric_forwarding_anycast_gateway features '
                                 ' are only available for SVIs.')
        args = dict(interface=interface, admin_state=admin_state,
                    description=description, mode=mode, ip_forward=ip_forward,
                    fabric_forwarding_anycast_gateway=fabric_forwarding_anycast_gateway)

        if intf_type == 'unknown':
            module.fail_json(msg='unknown interface type found-1',
                             interface=interface)

        existing, is_default = smart_existing(module, intf_type, normalized_interface)
        proposed = get_proposed(existing, normalized_interface, args)
    else:
        intf_type = normalized_interface = interface_type
        proposed = dict(interface_type=interface_type)

    commands = []
    if interface:
        delta = dict()

        if state == 'absent':
            if intf_type in ['svi', 'loopback', 'portchannel', 'nve']:
                if is_default != 'DNE':
                    cmds = ['no interface {0}'.format(normalized_interface)]
                    commands.append(cmds)
            elif intf_type in ['ethernet']:
                if is_default is False:
                    cmds = ['default interface {0}'.format(normalized_interface)]
                    commands.append(cmds)
        elif state == 'present':
            if not existing:
                cmds = get_interface_config_commands(proposed, normalized_interface, existing)
                commands.append(cmds)
            else:
                delta = dict(set(proposed.items()).difference(existing.items()))
                if delta:
                    cmds = get_interface_config_commands(delta, normalized_interface, existing)
                    commands.append(cmds)
        elif state == 'default':
            if is_default is False:
                cmds = ['default interface {0}'.format(normalized_interface)]
                commands.append(cmds)
            elif is_default == 'DNE':
                module.exit_json(msg='interface you are trying to default does not exist')
    elif interface_type:
        if state == 'present':
            module.fail_json(msg='The interface_type param can be used only with state absent.')

        existing = get_interfaces_dict(module)[interface_type]
        cmds = get_interface_type_removed_cmds(existing)
        commands.append(cmds)

    cmds = flatten_list(commands)
    end_state = existing

    if cmds:
        if module.check_mode:
            module.exit_json(changed=True, commands=cmds)
        else:
            load_config(module, cmds)
            results['changed'] = True
            if module.params['interface']:
                if delta.get('mode'):
                    # if the mode changes from L2 to L3, the admin state
                    # seems to change after the API call, so adding a second API
                    # call to ensure it's in the desired state.
                    admin_state = delta.get('admin_state') or admin_state
                    c1 = 'interface {0}'.format(normalized_interface)
                    c2 = get_admin_state(delta, normalized_interface, admin_state)
                    cmds2 = [c1, c2]
                    load_config(module, cmds2)
                    cmds.extend(cmds2)
                end_state, is_default = smart_existing(module, intf_type,
                                                       normalized_interface)
            else:
                end_state = get_interfaces_dict(module)[interface_type]
            cmds = [cmd for cmd in cmds if cmd != 'configure']

    results['commands'] = cmds

    module.exit_json(**results)