def _recursive_merge(conf, package):
    """Merge package into conf, recursively."""
    error = False
    for key, pack_conf in package.items():
        if isinstance(pack_conf, dict):
            if not pack_conf:
                continue
            conf[key] = conf.get(key, OrderedDict())
            error = _recursive_merge(conf=conf[key], package=pack_conf)

        elif isinstance(pack_conf, list):
            if not pack_conf:
                continue
            conf[key] = cv.ensure_list(conf.get(key))
            conf[key].extend(cv.ensure_list(pack_conf))

        else:
            if conf.get(key) is not None:
                return key
            else:
                conf[key] = pack_conf
    return error