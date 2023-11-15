def main():
    argument_spec = dict(
        name=dict(required=True),
        description=dict(default=''),
        job_type=dict(choices=['run', 'check', 'scan'], required=True),
        inventory=dict(default=''),
        project=dict(required=True),
        playbook=dict(required=True),
        credential=dict(default=''),
        vault_credential=dict(default=''),
        forks=dict(type='int'),
        limit=dict(default=''),
        verbosity=dict(type='int', choices=[0, 1, 2, 3, 4], default=0),
        extra_vars_path=dict(type='path', required=False),
        job_tags=dict(default=''),
        force_handlers_enabled=dict(type='bool', default=False),
        skip_tags=dict(default=''),
        start_at_task=dict(default=''),
        timeout=dict(type='int', default=0),
        fact_caching_enabled=dict(type='bool', default=False),
        host_config_key=dict(default=''),
        ask_diff_mode=dict(type='bool', default=False),
        ask_extra_vars=dict(type='bool', default=False),
        ask_limit=dict(type='bool', default=False),
        ask_tags=dict(type='bool', default=False),
        ask_skip_tags=dict(type='bool', default=False),
        ask_job_type=dict(type='bool', default=False),
        ask_verbosity=dict(type='bool', default=False),
        ask_inventory=dict(type='bool', default=False),
        ask_credential=dict(type='bool', default=False),
        survey_enabled=dict(type='bool', default=False),
        survey_spec=dict(type='dict', required=False),
        become_enabled=dict(type='bool', default=False),
        diff_mode_enabled=dict(type='bool', default=False),
        concurrent_jobs_enabled=dict(type='bool', default=False),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    module = TowerModule(argument_spec=argument_spec, supports_check_mode=True)

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