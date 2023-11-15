def delete_cache_contents(cmd, resource_group_name=None, item_name=None, resource_type=None):
    directory = _get_cache_directory(cmd.cli_ctx)
    item_path = os.path.join(directory, resource_group_name, resource_type, '{}.json'.format(item_name))
    try:
        os.remove(item_path)
    except OSError:
        logger.info('%s not found in object cache.', item_path)