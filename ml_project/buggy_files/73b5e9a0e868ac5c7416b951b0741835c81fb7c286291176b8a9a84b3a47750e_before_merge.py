def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(required=False),
        kind=dict(required=False, choices=KIND_CHOICES.keys()),
        inputs=dict(type='dict', required=False),
        injectors=dict(type='dict', required=False),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    module = TowerModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    name = module.params.get('name')
    kind = module.params.get('kind')
    state = module.params.get('state')

    json_output = {'credential_type': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        credential_type_res = tower_cli.get_resource('credential_type')

        params = {}
        params['name'] = name
        params['kind'] = kind
        params['managed_by_tower'] = False

        if module.params.get('description'):
            params['description'] = module.params.get('description')

        if module.params.get('inputs'):
            params['inputs'] = module.params.get('inputs')

        if module.params.get('injectors'):
            params['injectors'] = module.params.get('injectors')

        try:
            if state == 'present':
                params['create_on_missing'] = True
                result = credential_type_res.modify(**params)
                json_output['id'] = result['id']
            elif state == 'absent':
                params['fail_on_missing'] = False
                result = credential_type_res.delete(**params)

        except (exc.ConnectionError, exc.BadRequest) as excinfo:
            module.fail_json(
                msg='Failed to update credential type: {0}'.format(excinfo),
                changed=False
            )

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)