def acr_build_task_logs(cmd,
                        client,  # cf_acr_builds
                        registry_name,
                        build_id=None,
                        build_task_name=None,
                        image=None,
                        resource_group_name=None):
    _, resource_group_name = validate_managed_registry(
        cmd.cli_ctx, registry_name, resource_group_name, BUILD_TASKS_NOT_SUPPORTED)

    if not build_id:
        # show logs for the last build
        paged_builds = acr_build_task_list_builds(cmd,
                                                  client,
                                                  registry_name,
                                                  top=1,
                                                  build_task_name=build_task_name,
                                                  image=image)
        try:
            build_id = paged_builds.get(0)[0].build_id
            logger.warning(_get_list_builds_message(base_message="Showing logs of the last created build",
                                                    build_task_name=build_task_name,
                                                    image=image))
            logger.warning("Build ID: %s", build_id)
        except (AttributeError, KeyError, TypeError, IndexError):
            raise CLIError(_get_list_builds_message(base_message="Could not find the last created build",
                                                    build_task_name=build_task_name,
                                                    image=image))

    return acr_build_show_logs(client, build_id, registry_name, resource_group_name)