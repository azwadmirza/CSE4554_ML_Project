def _flatten(d):
    if not d:
        return defaultdict(lambda: None)

    if isinstance(d, dict):
        from flatten_json import flatten as fltn

        return defaultdict(lambda: None, fltn(d, "."))

    return defaultdict(lambda: "unable to parse")