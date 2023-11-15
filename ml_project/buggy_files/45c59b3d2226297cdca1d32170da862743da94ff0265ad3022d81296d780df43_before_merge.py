def cached_put(cmd_obj, operation, parameters, *args, **kwargs):
    def _put_operation():
        result = None
        if args:
            extended_args = args + (parameters,)
            result = operation(*extended_args)
        elif kwargs is not None:
            result = operation(parameters=parameters, **kwargs)
        return result

    cache_opt = cmd_obj.cli_ctx.data.get('_cache', '')
    write = 'write' in cache_opt
    write_through = 'write-through' in cache_opt

    if not write and not write_through:
        return _put_operation()

    cache_obj = CacheObject(cmd_obj, parameters.serialize(), operation)
    cache_obj.save(args, kwargs)

    if not write_through:
        return cache_obj
    return _put_operation()