def get_project(project_dir, config_path=None, project_name=None, verbose=False,
                host=None, tls_config=None, environment=None, override_dir=None):
    if not environment:
        environment = Environment.from_env_file(project_dir)
    config_details = config.find(project_dir, config_path, environment, override_dir)
    project_name = get_project_name(
        config_details.working_dir, project_name, environment
    )
    config_data = config.load(config_details)

    api_version = environment.get(
        'COMPOSE_API_VERSION',
        API_VERSIONS[config_data.version])

    client = get_client(
        verbose=verbose, version=api_version, tls_config=tls_config,
        host=host, environment=environment
    )

    global_parallel_limit = environment.get('COMPOSE_PARALLEL_LIMIT')
    if global_parallel_limit:
        global_parallel_limit = int(global_parallel_limit)

    with errors.handle_connection_errors(client):
        return Project.from_config(project_name, config_data, client,
                                   global_parallel_limit=global_parallel_limit)