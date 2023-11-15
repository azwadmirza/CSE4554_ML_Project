def project_from_options(project_dir, options):
    environment = Environment.from_env_file(project_dir)
    set_parallel_limit(environment)

    host = options.get('--host')
    if host is not None:
        host = host.lstrip('=')
    return get_project(
        project_dir,
        get_config_path_from_options(project_dir, options, environment),
        project_name=options.get('--project-name'),
        verbose=options.get('--verbose'),
        host=host,
        tls_config=tls_config_from_options(options),
        environment=environment,
        override_dir=options.get('--project-directory'),
    )