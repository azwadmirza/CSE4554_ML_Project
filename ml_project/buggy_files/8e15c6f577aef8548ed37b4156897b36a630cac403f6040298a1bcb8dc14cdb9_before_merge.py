def func(df, other, apply_func, call_queue_df=None, call_queue_other=None):
    if call_queue_df is not None and len(call_queue_df) > 0:
        for call, kwargs in call_queue_df:
            if isinstance(call, ray.ObjectID):
                call = ray.get(call)
            if isinstance(kwargs, ray.ObjectID):
                kwargs = ray.get(kwargs)
            df = call(df, **kwargs)
    if call_queue_other is not None and len(call_queue_other) > 0:
        for call, kwargs in call_queue_other:
            if isinstance(call, ray.ObjectID):
                call = ray.get(call)
            if isinstance(kwargs, ray.ObjectID):
                kwargs = ray.get(kwargs)
            other = call(other, **kwargs)
    return apply_func(df, other)