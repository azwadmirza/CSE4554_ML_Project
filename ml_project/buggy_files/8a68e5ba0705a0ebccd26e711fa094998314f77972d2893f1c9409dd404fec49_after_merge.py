def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        inventory=dict(required=True),
        enabled=dict(type='bool', default=True),
        variables=dict(),
        state=dict(choices=['present', 'absent'], default='present'),
    )
    module = TowerModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get('name')
    description = module.params.get('description')
    inventory = module.params.get('inventory')
    enabled = module.params.get('enabled')
    state = module.params.get('state')

    variables = module.params.get('variables')
    if variables:
        if variables.startswith('@'):
            filename = os.path.expanduser(variables[1:])
            with open(filename, 'r') as f:
                variables = f.read()

    json_output = {'host': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        host = tower_cli.get_resource('host')

        try:
            inv_res = tower_cli.get_resource('inventory')
            inv = inv_res.get(name=inventory)

            if state == 'present':
                result = host.modify(name=name, inventory=inv['id'], enabled=enabled,
                                     variables=variables, description=description, create_on_missing=True)
                json_output['id'] = result['id']
            elif state == 'absent':
                result = host.delete(name=name, inventory=inv['id'])
        except (exc.NotFound) as excinfo:
            module.fail_json(msg='Failed to update host, inventory not found: {0}'.format(excinfo), changed=False)
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            module.fail_json(msg='Failed to update host: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)