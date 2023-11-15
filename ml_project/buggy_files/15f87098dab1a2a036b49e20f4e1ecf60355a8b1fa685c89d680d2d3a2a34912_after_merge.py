def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    module = TowerModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get('name')
    description = module.params.get('description')
    state = module.params.get('state')

    json_output = {'organization': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        organization = tower_cli.get_resource('organization')
        try:
            if state == 'present':
                result = organization.modify(name=name, description=description, create_on_missing=True)
                json_output['id'] = result['id']
            elif state == 'absent':
                result = organization.delete(name=name)
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            module.fail_json(msg='Failed to update the organization: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)