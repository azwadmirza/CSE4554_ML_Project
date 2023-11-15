def show_cache_contents(cmd, resource_group_name=None, item_name=None, resource_type=None):
    directory = _get_cache_directory(cmd.cli_ctx)
    item_path = os.path.join(directory, resource_group_name, resource_type, '{}.json'.format(item_name))
    try:
        with open(item_path, 'r') as cache_file:
            cache_obj = json.loads(cache_file.read())
    except OSError:
        raise CLIError('Not found in cache: {}'.format(item_path))
    return cache_obj['_payload']