def main():
    argument_spec = dict(
        job_id=dict(type='int', required=True),
        timeout=dict(type='int'),
        min_interval=dict(type='float', default=1),
        max_interval=dict(type='float', default=30),
    )

    module = TowerModule(
        argument_spec,
        supports_check_mode=True
    )

    json_output = {}
    fail_json = None

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        job = tower_cli.get_resource('job')
        params = module.params.copy()

        # tower-cli gets very noisy when monitoring.
        # We pass in our our outfile to suppress the out during our monitor call.
        outfile = StringIO()
        params['outfile'] = outfile

        job_id = params.get('job_id')
        try:
            result = job.monitor(job_id, **params)
        except exc.Timeout as excinfo:
            result = job.status(job_id)
            result['id'] = job_id
            json_output['msg'] = 'Timeout waiting for job to finish.'
            json_output['timeout'] = True
        except exc.NotFound as excinfo:
            fail_json = dict(msg='Unable to wait, no job_id {0} found: {1}'.format(job_id, excinfo), changed=False)
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            fail_json = dict(msg='Unable to wait for job: {0}'.format(excinfo), changed=False)

    if fail_json is not None:
        module.fail_json(**fail_json)

    json_output['success'] = True
    for k in ('id', 'status', 'elapsed', 'started', 'finished'):
        json_output[k] = result.get(k)

    module.exit_json(**json_output)