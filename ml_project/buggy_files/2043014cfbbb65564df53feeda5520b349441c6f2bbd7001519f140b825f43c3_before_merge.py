def _recursive_merge(pack_name, comp_name, config, conf, package):
    """Merge package into conf, recursively."""
    for key, pack_conf in package.items():
        if isinstance(pack_conf, dict):
            if not pack_conf:
                continue
            conf[key] = conf.get(key, OrderedDict())
            _recursive_merge(pack_name, comp_name, config,
                             conf=conf[key], package=pack_conf)

        elif isinstance(pack_conf, list):
            if not pack_conf:
                continue
            conf[key] = cv.ensure_list(conf.get(key))
            conf[key].extend(cv.ensure_list(pack_conf))

        else:
            if conf.get(key) is not None:
                _log_pkg_error(
                    pack_name, comp_name, config,
                    'has keys that are defined multiple times')
            else:
                conf[key] = pack_conf