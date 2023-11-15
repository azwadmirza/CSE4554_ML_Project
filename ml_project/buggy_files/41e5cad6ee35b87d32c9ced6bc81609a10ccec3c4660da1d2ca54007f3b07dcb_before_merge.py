def inner_f(queue, func, **kwargs):  # pragma: no cover
    try:
        queue.put(func(**kwargs))
    except Exception as _e:
        import traceback

        traceback.print_exc()
        queue.put(None)