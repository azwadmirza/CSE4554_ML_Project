def inner_f(queue, func, *args, **kwargs):  # pragma: no cover
    try:
        queue.put(func(*args, **kwargs))
    except Exception:
        import traceback

        traceback.print_exc()
        queue.put(None)