def main():
    argument_spec = dict(
        status=dict(choices=['pending', 'waiting', 'running', 'error', 'failed', 'canceled', 'successful']),
        page=dict(type='int'),
        all_pages=dict(type='bool', default=False),
        query=dict(type='dict'),
    )

    module = TowerModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    json_output = {}

    query = module.params.get('query')
    status = module.params.get('status')
    page = module.params.get('page')
    all_pages = module.params.get('all_pages')

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        try:
            job = tower_cli.get_resource('job')
            params = {'status': status, 'page': page, 'all_pages': all_pages}
            if query:
                params['query'] = query.items()
            json_output = job.list(**params)
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            module.fail_json(msg='Failed to list jobs: {0}'.format(excinfo), changed=False)

    module.exit_json(**json_output)