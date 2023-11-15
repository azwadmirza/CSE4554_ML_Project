def acr_build_task_run(cmd,
                       client,  # cf_acr_builds
                       build_task_name,
                       registry_name,
                       no_format=False,
                       no_logs=False,
                       resource_group_name=None):
    _, resource_group_name = validate_managed_registry(
        cmd.cli_ctx, registry_name, resource_group_name, BUILD_TASKS_NOT_SUPPORTED)

    from ._client_factory import cf_acr_registries
    client_registries = cf_acr_registries(cmd.cli_ctx)

    queued_build = LongRunningOperation(cmd.cli_ctx)(
        client_registries.queue_build(resource_group_name,
                                      registry_name,
                                      BuildTaskBuildRequest(build_task_name=build_task_name)))

    build_id = queued_build.build_id
    logger.warning("Queued a build with build ID: %s", build_id)
    logger.warning("Waiting for build agent...")

    if no_logs:
        return get_build_with_polling(client, build_id, registry_name, resource_group_name)

    return acr_build_show_logs(client, build_id, registry_name, resource_group_name, no_format, True)