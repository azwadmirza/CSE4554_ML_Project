def main():
    argument_spec = tower_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True),
        description=dict(),
        job_type=dict(choices=['run', 'check', 'scan'], required=True),
        inventory=dict(),
        project=dict(required=True),
        playbook=dict(required=True),
        machine_credential=dict(),
        cloud_credential=dict(),
        network_credential=dict(),
        forks=dict(type='int'),
        limit=dict(),
        verbosity=dict(choices=['verbose', 'debug']),
        job_tags=dict(),
        skip_tags=dict(),
        host_config_key=dict(),
        extra_vars_path=dict(type='path', required=False),
        ask_extra_vars=dict(type='bool', default=False),
        ask_limit=dict(type='bool', default=False),
        ask_tags=dict(type='bool', default=False),
        ask_job_type=dict(type='bool', default=False),
        ask_inventory=dict(type='bool', default=False),
        ask_credential=dict(type='bool', default=False),
        become_enabled=dict(type='bool', default=False),
        state=dict(choices=['present', 'absent'], default='present'),
    ))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_TOWER_CLI:
        module.fail_json(msg='ansible-tower-cli required for this module')

    name = module.params.get('name')
    state = module.params.pop('state')
    json_output = {'job_template': name, 'state': state}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        jt = tower_cli.get_resource('job_template')

        params = update_resources(module, module.params)
        params = update_fields(params)
        params['create_on_missing'] = True

        try:
            if state == 'present':
                result = jt.modify(**params)
                json_output['id'] = result['id']
            elif state == 'absent':
                result = jt.delete(**params)
        except (exc.ConnectionError, exc.BadRequest, exc.NotFound) as excinfo:
            module.fail_json(msg='Failed to update job template: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)