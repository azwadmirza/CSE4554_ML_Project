def main():
    argument_spec = dict(
        job_id=dict(type='int', required=True),
        fail_if_not_running=dict(type='bool', default=False),
    )

    module = TowerModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    job_id = module.params.get('job_id')
    json_output = {}

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        job = tower_cli.get_resource('job')
        params = module.params.copy()

        try:
            result = job.cancel(job_id, **params)
            json_output['id'] = job_id
        except (exc.ConnectionError, exc.BadRequest, exc.TowerCLIError, exc.AuthError) as excinfo:
            module.fail_json(msg='Unable to cancel job_id/{0}: {1}'.format(job_id, excinfo), changed=False)

    json_output['changed'] = result['changed']
    json_output['status'] = result['status']
    module.exit_json(**json_output)