def _flatten_deferred_list(deferreds):
    """Given a list of deferreds, either return the single deferred,
    combine into a DeferredList, or return an already resolved deferred.
    """
    if len(deferreds) > 1:
        return DeferredList(deferreds, fireOnOneErrback=True, consumeErrors=True)
    elif len(deferreds) == 1:
        return deferreds[0]
    else:
        return defer.succeed(None)