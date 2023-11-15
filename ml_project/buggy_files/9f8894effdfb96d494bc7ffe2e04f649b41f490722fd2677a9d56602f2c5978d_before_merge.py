def create_function(cmd, resource_group_name, name, storage_account, plan=None,
                    consumption_plan_location=None, deployment_source_url=None,
                    deployment_source_branch='master', deployment_local_git=None,
                    deployment_container_image_name=None):
    if deployment_source_url and deployment_local_git:
        raise CLIError('usage error: --deployment-source-url <url> | --deployment-local-git')
    if bool(plan) == bool(consumption_plan_location):
        raise CLIError("usage error: --plan NAME_OR_ID | --consumption-plan-location LOCATION")

    site_config = SiteConfig(app_settings=[])
    functionapp_def = Site(location=None, site_config=site_config)
    client = web_client_factory(cmd.cli_ctx)

    if consumption_plan_location:
        locations = list_consumption_locations(cmd)
        location = next((l for l in locations if l['name'].lower() == consumption_plan_location.lower()), None)
        if location is None:
            raise CLIError("Location is invalid. Use: az functionapp list-consumption-locations")
        functionapp_def.location = consumption_plan_location
        functionapp_def.kind = 'functionapp'
    else:
        if is_valid_resource_id(plan):
            plan = parse_resource_id(plan)['name']
        plan_info = client.app_service_plans.get(resource_group_name, plan)
        location = plan_info.location
        is_linux = plan_info.reserved
        if is_linux:
            functionapp_def.kind = 'functionapp,linux'
            site_config.app_settings.append(NameValuePair('FUNCTIONS_EXTENSION_VERSION', 'beta'))
            site_config.app_settings.append(NameValuePair('MACHINEKEY_DecryptionKey',
                                                          str(hexlify(urandom(32)).decode()).upper()))
            if deployment_container_image_name:
                site_config.app_settings.append(NameValuePair('DOCKER_CUSTOM_IMAGE_NAME',
                                                              deployment_container_image_name))
                site_config.app_settings.append(NameValuePair('FUNCTION_APP_EDIT_MODE', 'readOnly'))
                site_config.app_settings.append(NameValuePair('WEBSITES_ENABLE_APP_SERVICE_STORAGE', 'false'))
            else:
                site_config.app_settings.append(NameValuePair('WEBSITES_ENABLE_APP_SERVICE_STORAGE', 'true'))
                site_config.linux_fx_version = 'DOCKER|appsvc/azure-functions-runtime'
        else:
            functionapp_def.kind = 'functionapp'
            site_config.app_settings.append(NameValuePair('FUNCTIONS_EXTENSION_VERSION', '~1'))

        functionapp_def.server_farm_id = plan
        functionapp_def.location = location

    con_string = _validate_and_get_connection_string(cmd.cli_ctx, resource_group_name, storage_account)

    # adding appsetting to site to make it a function
    site_config.app_settings.append(NameValuePair('AzureWebJobsStorage', con_string))
    site_config.app_settings.append(NameValuePair('AzureWebJobsDashboard', con_string))
    site_config.app_settings.append(NameValuePair('WEBSITE_NODE_DEFAULT_VERSION', '6.5.0'))

    if consumption_plan_location is None:
        site_config.always_on = True
    else:
        site_config.app_settings.append(NameValuePair('WEBSITE_CONTENTAZUREFILECONNECTIONSTRING',
                                                      con_string))
        site_config.app_settings.append(NameValuePair('WEBSITE_CONTENTSHARE', name.lower()))

    poller = client.web_apps.create_or_update(resource_group_name, name, functionapp_def)
    functionapp = LongRunningOperation(cmd.cli_ctx)(poller)

    _set_remote_or_local_git(cmd, functionapp, resource_group_name, name, deployment_source_url,
                             deployment_source_branch, deployment_local_git)

    return functionapp