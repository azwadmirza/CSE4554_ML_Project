def producer(obj, func, results, limiter):
    """
    The entry point for a producer thread which runs func on a single object.
    Places a tuple on the results queue once func has either returned or raised.
    """
    with limiter, global_limiter:
        try:
            result = func(obj)
            results.put((obj, result, None))
        except Exception as e:
            results.put((obj, None, e))