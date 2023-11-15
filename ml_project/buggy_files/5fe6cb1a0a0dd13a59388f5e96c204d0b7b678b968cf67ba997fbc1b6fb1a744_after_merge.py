def deploy_func(df, apply_func, call_queue_df=None, call_queues_other=None, *others):
    if call_queue_df is not None and len(call_queue_df) > 0:
        for call, kwargs in call_queue_df:
            if isinstance(call, bytes):
                call = pkl.loads(call)
            if isinstance(kwargs, bytes):
                kwargs = pkl.loads(kwargs)
            df = call(df, **kwargs)
    new_others = np.empty(shape=len(others), dtype=object)
    for i, call_queue_other in enumerate(call_queues_other):
        other = others[i]
        if call_queue_other is not None and len(call_queue_other) > 0:
            for call, kwargs in call_queue_other:
                if isinstance(call, bytes):
                    call = pkl.loads(call)
                if isinstance(kwargs, bytes):
                    kwargs = pkl.loads(kwargs)
                other = call(other, **kwargs)
        new_others[i] = other
    if isinstance(apply_func, bytes):
        apply_func = pkl.loads(apply_func)
    return apply_func(df, new_others)