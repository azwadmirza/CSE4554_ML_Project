def hash_params(params):
    if not isinstance(params, dict):
        return params
    else:
        s = set()
        for k,v in iteritems(params):
            if isinstance(v, dict):
                s.update((k, hash_params(v)))
            elif isinstance(v, list):
                things = []
                for item in v:
                    things.append(hash_params(item))
                s.update((k, tuple(things)))
            else:
                s.update((k, v))
        return frozenset(s)