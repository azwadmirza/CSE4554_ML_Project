def create_webapp(cmd, resource_group_name, name, plan, runtime=None, startup_file=None,
                  deployment_container_image_name=None, deployment_source_url=None, deployment_source_branch='master',
                  deployment_local_git=None):
    if deployment_source_url and deployment_local_git:
        raise CLIError('usage error: --deployment-source-url <url> | --deployment-local-git')
    client = web_client_factory(cmd.cli_ctx)
    if is_valid_resource_id(plan):
        parse_result = parse_resource_id(plan)
        plan_info = client.app_service_plans.get(parse_result['resource_group'], parse_result['name'])
    else:
        plan_info = client.app_service_plans.get(resource_group_name, plan)
    is_linux = plan_info.reserved
    node_default_version = "6.9.1"
    location = plan_info.location
    site_config = SiteConfig(app_settings=[])
    webapp_def = Site(server_farm_id=plan_info.id, location=location, site_config=site_config)
    helper = _StackRuntimeHelper(client, linux=is_linux)

    if is_linux:
        if runtime and deployment_container_image_name:
            raise CLIError('usage error: --runtime | --deployment-container-image-name')
        if startup_file:
            site_config.app_command_line = startup_file

        if runtime:
            site_config.linux_fx_version = runtime
            match = helper.resolve(runtime)
            if not match:
                raise CLIError("Linux Runtime '{}' is not supported."
                               "Please invoke 'list-runtimes' to cross check".format(runtime))

        elif deployment_container_image_name:
            site_config.linux_fx_version = _format_linux_fx_version(deployment_container_image_name)
            site_config.app_settings.append(NameValuePair("WEBSITES_ENABLE_APP_SERVICE_STORAGE", "false"))
        else:  # must specify runtime
            raise CLIError('usage error: must specify --runtime | --deployment-container-image-name')  # pylint: disable=line-too-long

    elif runtime:  # windows webapp with runtime specified
        if startup_file or deployment_container_image_name:
            raise CLIError("usage error: --startup-file or --deployment-container-image-name is "
                           "only appliable on linux webapp")
        match = helper.resolve(runtime)
        if not match:
            raise CLIError("Runtime '{}' is not supported. Please invoke 'list-runtimes' to cross check".format(runtime))  # pylint: disable=line-too-long
        match['setter'](match, site_config)
        # Be consistent with portal: any windows webapp should have this even it doesn't have node in the stack
        if not match['displayName'].startswith('node'):
            site_config.app_settings.append(NameValuePair("WEBSITE_NODE_DEFAULT_VERSION",
                                                          node_default_version))

    else:  # windows webapp without runtime specified
        site_config.app_settings.append(NameValuePair("WEBSITE_NODE_DEFAULT_VERSION",
                                                      node_default_version))

    if site_config.app_settings:
        for setting in site_config.app_settings:
            logger.info('Will set appsetting %s', setting)

    poller = client.web_apps.create_or_update(resource_group_name, name, webapp_def)
    webapp = LongRunningOperation(cmd.cli_ctx)(poller)

    # Ensure SCC operations follow right after the 'create', no precedent appsetting update commands
    _set_remote_or_local_git(cmd, webapp, resource_group_name, name, deployment_source_url,
                             deployment_source_branch, deployment_local_git)

    _fill_ftp_publishing_url(cmd, webapp, resource_group_name, name)

    return webapp