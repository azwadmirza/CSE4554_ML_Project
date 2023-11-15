def delete_resource(resource_ids=None, resource_group_name=None,
                    resource_provider_namespace=None, parent_resource_path=None, resource_type=None,
                    resource_name=None, api_version=None):
    """
    Deletes the given resource(s).
    This function allows deletion of ids with dependencies on one another.
    This is done with multiple passes through the given ids.
    """
    parsed_ids = _get_parsed_resource_ids(resource_ids) or [_create_parsed_id(resource_group_name,
                                                                              resource_provider_namespace,
                                                                              parent_resource_path,
                                                                              resource_type,
                                                                              resource_name)]
    to_be_deleted = [(_get_rsrc_util_from_parsed_id(id_dict, api_version), id_dict) for id_dict in parsed_ids]

    results = []
    from msrestazure.azure_exceptions import CloudError
    while to_be_deleted:
        logger.debug("Start new loop to delete resources.")
        operations = []
        failed_to_delete = []
        for rsrc_utils, id_dict in to_be_deleted:
            try:
                operations.append(rsrc_utils.delete())
                logger.debug("deleting", resource_dict_to_id(**id_dict))
            except CloudError as e:
                # request to delete failed, add parsed id dict back to queue
                id_dict['exception'] = str(e)
                failed_to_delete.append((rsrc_utils, id_dict))
        to_be_deleted = failed_to_delete

        # stop deleting if none deletable
        if not operations:
            break

        # all operations return result before next pass
        for operation in operations:
            results.append(operation.result())

    if to_be_deleted:
        error_msg_builder = ['Some resources failed to be deleted:']
        for _, id_dict in to_be_deleted:
            logger.debug(id_dict['exception'])
            error_msg_builder.append(resource_dict_to_id(**id_dict))
        raise CLIError(os.linesep.join(error_msg_builder))

    return _single_or_collection(results)