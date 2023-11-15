def _maybe_resolve_exprs(table, exprs):
    try:
        return table._resolve(exprs)
    except (AttributeError, IbisTypeError):
        return None