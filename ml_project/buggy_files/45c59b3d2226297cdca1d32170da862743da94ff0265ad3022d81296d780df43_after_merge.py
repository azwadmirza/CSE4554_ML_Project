def cached_put(cmd_obj, operation, parameters, *args, **kwargs):

    def _put_operation():
        result = None
        if args:
            extended_args = args + (parameters,)
            result = operation(*extended_args)
        elif kwargs is not None:
            result = operation(parameters=parameters, **kwargs)
        return result

    # early out if the command does not use the cache
    if not cmd_obj.command_kwargs.get('supports_local_cache', False):
        return _put_operation()

    use_cache = cmd_obj.cli_ctx.data.get('_cache', False)
    if not use_cache:
        result = _put_operation()

    cache_obj = CacheObject(cmd_obj, parameters.serialize(), operation)
    if use_cache:
        cache_obj.save(args, kwargs)
        return cache_obj

    # for a successful PUT, attempt to delete the cache file
    obj_dir, obj_file = cache_obj.path(args, kwargs)
    obj_path = os.path.join(obj_dir, obj_file)
    try:
        os.remove(obj_path)
    except (OSError, IOError):  # FileNotFoundError introduced in Python 3
        pass
    return result