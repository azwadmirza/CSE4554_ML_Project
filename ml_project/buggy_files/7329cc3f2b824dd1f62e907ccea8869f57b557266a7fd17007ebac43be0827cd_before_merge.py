def create_deploy_webapp(cmd, name, location=None, sku=None, dryrun=False):  # pylint: disable=too-many-statements
    import os
    client = web_client_factory(cmd.cli_ctx)
    # the code to deploy is expected to be the current directory the command is running from
    src_dir = os.getcwd()
    # if dir is empty, show a message in dry run
    do_deployment = False if os.listdir(src_dir) == [] else True
    _create_new_rg = True
    _create_new_asp = True
    _create_new_app = True
    _set_build_app_setting = False

    # determine the details for app to be created from src contents
    lang_details = get_lang_from_content(src_dir)
    # we support E2E create and deploy for selected stacks, any other stack, set defaults for os & runtime
    # and skip deployment
    if lang_details['language'] is None:
        do_deployment = False
        sku = sku | 'F1'
        os_val = OS_DEFAULT
        detected_version = '-'
        runtime_version = '-'
    else:
        # update SKU to user set value
        if sku is None:
            sku = lang_details.get("default_sku")
        else:
            sku = sku
        language = lang_details.get("language")
        is_skip_build = language.lower() == STATIC_RUNTIME_NAME
        os_val = "Linux" if language.lower() == NODE_RUNTIME_NAME \
            or language.lower() == PYTHON_RUNTIME_NAME else OS_DEFAULT
        # detect the version
        data = get_runtime_version_details(lang_details.get('file_loc'), language)
        version_used_create = data.get('to_create')
        detected_version = data.get('detected')
        runtime_version = "{}|{}".format(language, version_used_create) if \
            version_used_create != "-" else version_used_create

    full_sku = get_sku_name(sku)
    location = set_location(cmd, sku, location)
    loc_name = location.replace(" ", "").lower()
    is_linux = True if os_val == 'Linux' else False
    asp = "appsvc_asp_{}_{}".format(os_val, loc_name)
    rg_name = "appsvc_rg_{}_{}".format(os_val, loc_name)
    # Resource group: check if default RG is set
    default_rg = cmd.cli_ctx.config.get('defaults', 'group', fallback=None)
    _create_new_rg = should_create_new_rg(cmd, default_rg, rg_name, is_linux)

    src_path = "{}".format(src_dir.replace("\\", "\\\\"))
    rg_str = "{}".format(rg_name)
    dry_run_str = r""" {
            "name" : "%s",
            "serverfarm" : "%s",
            "resourcegroup" : "%s",
            "sku": "%s",
            "os": "%s",
            "location" : "%s",
            "src_path" : "%s",
            "version_detected": "%s",
            "version_to_create": "%s"
            }
            """ % (name, asp, rg_str, full_sku, os_val, location, src_path,
                   detected_version, runtime_version)
    create_json = json.loads(dry_run_str)

    if dryrun:
        logger.warning("Web app will be created with the below configuration,re-run command "
                       "without the --dryrun flag to create & deploy a new app")
        return create_json

    # create RG if the RG doesn't already exist
    if _create_new_rg:
        logger.warning("Creating Resource group '%s' ...", rg_name)
        create_resource_group(cmd, rg_name, location)
        logger.warning("Resource group creation complete")
        _create_new_asp = True
    else:
        logger.warning("Resource group '%s' already exists.", rg_name)
        _create_new_asp = should_create_new_asp(cmd, rg_name, asp, location)
    # create new ASP if an existing one cannot be used
    if _create_new_asp:
        logger.warning("Creating App service plan '%s' ...", asp)
        sku_def = SkuDescription(tier=full_sku, name=sku, capacity=(1 if is_linux else None))
        plan_def = AppServicePlan(location=loc_name, app_service_plan_name=asp,
                                  sku=sku_def, reserved=(is_linux or None))
        client.app_service_plans.create_or_update(rg_name, asp, plan_def)
        logger.warning("App service plan creation complete")
        _create_new_app = True
        _show_too_many_apps_warn = False
    else:
        logger.warning("App service plan '%s' already exists.", asp)
        _show_too_many_apps_warn = get_num_apps_in_asp(cmd, rg_name, asp) > 5
        _create_new_app = should_create_new_app(cmd, rg_name, name)
    # create the app
    if _create_new_app:
        logger.warning("Creating app '%s' ....", name)
        create_webapp(cmd, rg_name, name, asp, runtime_version if is_linux else None)
        logger.warning("Webapp creation complete")
        _set_build_app_setting = True
        if _show_too_many_apps_warn:
            logger.warning("There are sites that have been deployed to the same hosting "
                           "VM of this region, to prevent performance impact please "
                           "delete existing site(s) or switch to a different default resource group "
                           "using 'az configure' command")
    else:
        logger.warning("App '%s' already exists", name)
        # for an existing app check if the runtime version needs to be updated
        # Get site config to check the runtime version
        site_config = client.web_apps.get_configuration(rg_name, name)
        if os_val == 'Linux' and site_config.linux_fx_version != runtime_version:
            logger.warning('Updating runtime version from %s to %s',
                           site_config.linux_fx_version, runtime_version)
            update_site_configs(cmd, rg_name, name, linux_fx_version=runtime_version)
        elif os_val == 'Windows' and site_config.windows_fx_version != runtime_version:
            logger.warning('Updating runtime version from %s to %s',
                           site_config.windows_fx_version, runtime_version)
            update_site_configs(cmd, rg_name, name, windows_fx_version=runtime_version)

        if do_deployment and not is_skip_build:
            _set_build_app_setting = True
            # setting the appsettings causes a app restart so we avoid if not needed
            application_settings = client.web_apps.list_application_settings(rg_name, name)
            _app_settings = application_settings.properties
            for key, value in _app_settings.items():
                if key.upper() == 'SCM_DO_BUILD_DURING_DEPLOYMENT' and value.upper() == "FALSE":
                    _set_build_app_setting = False

    # update create_json to include the app_url
    url = _get_url(cmd, rg_name, name)
    if _set_build_app_setting:
        # setting to build after deployment
        logger.warning("Updating app settings to enable build after deployment")
        update_app_settings(cmd, rg_name, name, ["SCM_DO_BUILD_DURING_DEPLOYMENT=true"])

    if do_deployment:
        logger.warning("Creating zip with contents of dir %s ...", src_dir)
        # zip contents & deploy
        zip_file_path = zip_contents_from_dir(src_dir, language)

        logger.warning("Preparing to deploy %s contents to app."
                       "This operation can take a while to complete ...",
                       '' if is_skip_build else 'and build')
        enable_zip_deploy(cmd, rg_name, name, zip_file_path)
        # Remove the file after deployment, handling exception if user removed the file manually
        try:
            os.remove(zip_file_path)
        except OSError:
            pass
    create_json.update({'app_url': url})
    logger.warning("All done.")
    return create_json