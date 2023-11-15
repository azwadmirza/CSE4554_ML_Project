def main():
    argument_spec = dict(
        job_template=dict(required=True),
        job_type=dict(choices=['run', 'check', 'scan']),
        inventory=dict(),
        credential=dict(),
        limit=dict(),
        tags=dict(type='list'),
        extra_vars=dict(type='list'),
    )

    module = TowerModule(
        argument_spec,
        supports_check_mode=True
    )

    json_output = {}
    tags = module.params.get('tags')

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        try:
            params = module.params.copy()
            if isinstance(tags, list):
                params['tags'] = ','.join(tags)
            job = tower_cli.get_resource('job')

            lookup_fields = ('job_template', 'inventory', 'credential')
            for field in lookup_fields:
                try:
                    name = params.pop(field)
                    result = tower_cli.get_resource(field).get(name=name)
                    params[field] = result['id']
                except exc.NotFound as excinfo:
                    module.fail_json(msg='Unable to launch job, {0}/{1} was not found: {2}'.format(field, name, excinfo), changed=False)

            result = job.launch(no_input=True, **params)
            json_output['id'] = result['id']
            json_output['status'] = result['status']
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            module.fail_json(msg='Unable to launch job: {0}'.format(excinfo), changed=False)

    json_output['changed'] = result['changed']
    module.exit_json(**json_output)