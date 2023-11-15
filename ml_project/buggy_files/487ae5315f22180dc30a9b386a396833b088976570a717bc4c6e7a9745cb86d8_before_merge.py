def acr_build(cmd,
              client,
              registry_name,
              source_location,
              image_names=None,
              resource_group_name=None,
              timeout=None,
              build_arg=None,
              secret_build_arg=None,
              docker_file_path='Dockerfile',
              no_push=False,
              no_logs=False,
              os_type='Linux'):
    _, resource_group_name = validate_managed_registry(
        cmd.cli_ctx, registry_name, resource_group_name, BUILD_NOT_SUPPORTED)

    client_registries = cf_acr_registries(cmd.cli_ctx)

    tar_file_path = os.path.join(tempfile.gettempdir(), 'source_archive_{}.tar.gz'.format(hash(os.times())))

    if os.path.exists(source_location):
        if not os.path.isdir(source_location):
            raise CLIError("Source location should be a local directory path or remote URL.")

        _check_local_docker_file(source_location, docker_file_path)

        try:
            source_location = _upload_source_code(
                client_registries, registry_name, resource_group_name, source_location, tar_file_path, docker_file_path)
        except Exception as err:
            raise CLIError(err)
        finally:
            try:
                logger.debug("Deleting the archived source code from '%s'.", tar_file_path)
                os.remove(tar_file_path)
            except OSError:
                pass
    else:
        source_location = _check_remote_source_code(source_location)
        logger.warning("Sending build context to ACR...")

    if no_push:
        is_push_enabled = False
    else:
        if image_names:
            is_push_enabled = True
        else:
            is_push_enabled = False
            logger.warning("'--image -t' is not provided. Skipping image push after build.")

    build_request = QuickBuildRequest(
        source_location=source_location,
        platform=PlatformProperties(os_type=os_type),
        docker_file_path=docker_file_path,
        image_names=image_names,
        is_push_enabled=is_push_enabled,
        timeout=timeout,
        build_arguments=(build_arg if build_arg else []) + (secret_build_arg if secret_build_arg else []))

    queued_build = LongRunningOperation(cmd.cli_ctx)(client_registries.queue_build(
        resource_group_name=resource_group_name,
        registry_name=registry_name,
        build_request=build_request))

    build_id = queued_build.build_id
    logger.warning("Queued a build with build ID: %s", build_id)
    logger.warning("Waiting for build agent...")

    if no_logs:
        return get_build_with_polling(client, build_id, registry_name, resource_group_name)

    return acr_build_show_logs(client, build_id, registry_name, resource_group_name, True)