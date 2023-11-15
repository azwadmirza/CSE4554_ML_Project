def deploy_func(df, other, apply_func, call_queue_df=None, call_queue_other=None):
    if call_queue_df is not None and len(call_queue_df) > 0:
        for call, kwargs in call_queue_df:
            if isinstance(call, bytes):
                call = pkl.loads(call)
            if isinstance(kwargs, bytes):
                kwargs = pkl.loads(kwargs)
            df = call(df, **kwargs)
    if call_queue_other is not None and len(call_queue_other) > 0:
        for call, kwargs in call_queue_other:
            if isinstance(call, bytes):
                call = pkl.loads(call)
            if isinstance(kwargs, bytes):
                kwargs = pkl.loads(kwargs)
            other = call(other, **kwargs)
    if isinstance(apply_func, bytes):
        apply_func = pkl.loads(apply_func)
    return apply_func(df, other)