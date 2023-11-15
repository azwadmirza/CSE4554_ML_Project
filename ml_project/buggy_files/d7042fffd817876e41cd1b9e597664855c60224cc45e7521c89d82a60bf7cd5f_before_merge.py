def cached_get(cmd_obj, operation, *args, **kwargs):

    def _get_operation():
        result = None
        if args:
            result = operation(*args)
        elif kwargs is not None:
            result = operation(**kwargs)
        return result

    cache_opt = cmd_obj.cli_ctx.data.get('_cache', '')
    if 'read' not in cache_opt:
        return _get_operation()

    cache_obj = CacheObject(cmd_obj, None, operation)
    try:
        cache_obj.load(args, kwargs)
        return cache_obj
    except (OSError, IOError):  # FileNotFoundError introduced in Python 3
        message = "{model} '{name}' not found in cache. Retrieving from Azure...".format(**cache_obj.prop_dict())
        logger.warning(message)
        return _get_operation()
    except t_JSONDecodeError:
        message = "{model} '{name}' found corrupt in cache. Retrieving from Azure...".format(**cache_obj.prod_dict())
        logger.warning(message)
        return _get_operation()