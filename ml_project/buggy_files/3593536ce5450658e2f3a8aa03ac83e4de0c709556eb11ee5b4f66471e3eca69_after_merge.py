def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        inventory=dict(required=True),
        variables=dict(),
        credential=dict(),
        source=dict(choices=["manual", "file", "ec2", "rax", "vmware",
                             "gce", "azure", "azure_rm", "openstack",
                             "satellite6", "cloudforms", "custom"], default="manual"),
        source_regions=dict(),
        source_vars=dict(),
        instance_filters=dict(),
        group_by=dict(),
        source_script=dict(),
        overwrite=dict(type='bool', default=False),
        overwrite_vars=dict(),
        update_on_launch=dict(type='bool', default=False),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    module = TowerModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get('name')
    inventory = module.params.get('inventory')
    credential = module.params.get('credential')
    state = module.params.pop('state')

    variables = module.params.get('variables')
    if variables:
        if variables.startswith('@'):
            filename = os.path.expanduser(variables[1:])
            with open(filename, 'r') as f:
                variables = f.read()

    json_output = {'group': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        group = tower_cli.get_resource('group')
        try:
            params = module.params.copy()
            params['create_on_missing'] = True
            params['variables'] = variables

            inv_res = tower_cli.get_resource('inventory')
            inv = inv_res.get(name=inventory)
            params['inventory'] = inv['id']

            if credential:
                cred_res = tower_cli.get_resource('credential')
                cred = cred_res.get(name=credential)
                params['credential'] = cred['id']

            if state == 'present':
                result = group.modify(**params)
                json_output['id'] = result['id']
            elif state == 'absent':
                result = group.delete(**params)
        except (exc.NotFound) as excinfo:
            module.fail_json(msg='Failed to update the group, inventory not found: {0}'.format(excinfo), changed=False)
        except (exc.ConnectionError, exc.BadRequest, exc.NotFound, exc.AuthError) as excinfo:
            module.fail_json(msg='Failed to update the group: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)