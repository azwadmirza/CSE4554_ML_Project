def main():
    """ Entry point for ansible module. """
    argument_spec = {
        'state': {'default': 'present', 'choices': ['present', 'absent']},
        'table': {'required': True},
        'record': {'required': True},
        'col': {'required': True},
        'key': {'required': False},
        'value': {'required': True},
        'timeout': {'default': 5, 'type': 'int'},
    }

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    result = {'changed': False}

    # We add ovs-vsctl to module_params to later build up templatized commands
    module.params["ovs-vsctl"] = module.get_bin_path("ovs-vsctl", True)

    want = map_params_to_obj(module)
    have = map_config_to_obj(module)

    commands = map_obj_to_commands(want, have, module)
    result['commands'] = commands

    if commands:
        if not module.check_mode:
            for c in commands:
                module.run_command(c, check_rc=True)
        result['changed'] = True

    module.exit_json(**result)