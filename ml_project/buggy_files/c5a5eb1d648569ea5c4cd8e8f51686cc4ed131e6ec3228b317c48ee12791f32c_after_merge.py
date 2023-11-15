def concretize(obj):
    if isinstance(obj, dict):
        # make sure that there's no hidden caveat
        ret = dict()
        for k, v in obj.items():
            ret[concretize(k)] = concretize(v)
        return ret
    elif isinstance(obj, (list, tuple)):
        return obj.__class__(list(map(concretize, obj)))
    else:
        return obj