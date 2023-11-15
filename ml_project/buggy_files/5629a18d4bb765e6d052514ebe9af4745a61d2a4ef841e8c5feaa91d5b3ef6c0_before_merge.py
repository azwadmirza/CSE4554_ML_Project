def _clean_log(obj):
    # Fixes https://github.com/ray-project/ray/issues/10631
    if isinstance(obj, dict):
        return {k: _clean_log(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_log(v) for v in obj]

    # Else
    try:
        pickle.dumps(obj)
        return obj
    except Exception:
        # give up, similar to _SafeFallBackEncoder
        return str(obj)