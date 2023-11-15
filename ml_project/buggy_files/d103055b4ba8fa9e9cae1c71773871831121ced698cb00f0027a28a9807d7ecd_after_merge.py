def _flatten(d):
    if not d:
        return defaultdict(lambda: None)

    if isinstance(d, dict):
        return defaultdict(lambda: None, flatten(d))

    return defaultdict(lambda: "unable to parse")