def delete_cache_contents(cmd, resource_group_name, item_name, resource_type):
    directory = _get_cache_directory(cmd.cli_ctx)
    item_path = os.path.join(directory, resource_group_name, resource_type, '{}.json'.format(item_name))
    try:
        os.remove(item_path)
    except (OSError, IOError):
        logger.info('%s not found in object cache.', item_path)