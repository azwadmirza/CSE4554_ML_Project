def acr_build_show_logs(client,
                        build_id,
                        registry_name,
                        resource_group_name,
                        no_format=False,
                        raise_error_on_failure=False):
    log_file_sas = None
    error_message = "Could not get build logs for build ID: {}.".format(build_id)
    try:
        build_log_result = client.get_log_link(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            build_id=build_id)
        log_file_sas = build_log_result.log_link
    except (AttributeError, CloudError) as e:
        logger.debug("%s Exception: %s", error_message, e)
        raise CLIError(error_message)

    if not log_file_sas:
        logger.debug("%s Empty SAS URL.", error_message)
        raise CLIError(error_message)

    account_name, endpoint_suffix, container_name, blob_name, sas_token = _get_blob_info(log_file_sas)

    _stream_logs(no_format,
                 byte_size=1024,  # 1 KiB
                 timeout_in_seconds=1800,  # 30 minutes
                 blob_service=AppendBlobService(
                     account_name=account_name,
                     sas_token=sas_token,
                     endpoint_suffix=endpoint_suffix),
                 container_name=container_name,
                 blob_name=blob_name,
                 raise_error_on_failure=raise_error_on_failure)