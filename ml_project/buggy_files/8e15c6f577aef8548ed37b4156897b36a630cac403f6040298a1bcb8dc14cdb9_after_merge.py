def func(df, apply_func, call_queue_df=None, call_queues_other=None, *others):
    if call_queue_df is not None and len(call_queue_df) > 0:
        for call, kwargs in call_queue_df:
            if isinstance(call, ray.ObjectID):
                call = ray.get(call)
            if isinstance(kwargs, ray.ObjectID):
                kwargs = ray.get(kwargs)
            df = call(df, **kwargs)
    new_others = np.empty(shape=len(others), dtype=object)
    for i, call_queue_other in enumerate(call_queues_other):
        other = others[i]
        if call_queue_other is not None and len(call_queue_other) > 0:
            for call, kwargs in call_queue_other:
                if isinstance(call, ray.ObjectID):
                    call = ray.get(call)
                if isinstance(kwargs, ray.ObjectID):
                    kwargs = ray.get(kwargs)
                other = call(other, **kwargs)
        new_others[i] = other
    return apply_func(df, new_others)