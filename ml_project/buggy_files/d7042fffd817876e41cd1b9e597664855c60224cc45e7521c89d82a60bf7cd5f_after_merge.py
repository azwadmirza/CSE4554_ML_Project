def cached_get(cmd_obj, operation, *args, **kwargs):

    def _get_operation():
        result = None
        if args:
            result = operation(*args)
        elif kwargs is not None:
            result = operation(**kwargs)
        return result

    # early out if the command does not use the cache
    if not cmd_obj.command_kwargs.get('supports_local_cache', False):
        return _get_operation()

    cache_obj = CacheObject(cmd_obj, None, operation)
    try:
        cache_obj.load(args, kwargs)
        if _is_stale(cmd_obj.cli_ctx, cache_obj):
            message = "{model} '{name}' stale in cache. Retrieving from Azure...".format(**cache_obj.prop_dict())
            logger.warning(message)
            return _get_operation()
        return cache_obj
    except Exception:  # pylint: disable=broad-except
        message = "{model} '{name}' not found in cache. Retrieving from Azure...".format(**cache_obj.prop_dict())
        logger.debug(message)
        return _get_operation()