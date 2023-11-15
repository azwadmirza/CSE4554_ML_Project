def only_once(fn):
    """Decorate the given function to be a no-op after it is called exactly
    once."""

    once = [fn]

    def go(*arg, **kw):
        # strong reference fn so that it isn't garbage collected,
        # which interferes with the event system's expectations
        strong_fn = fn  # noqa
        if once:
            once_fn = once.pop()
            return once_fn(*arg, **kw)

    return go