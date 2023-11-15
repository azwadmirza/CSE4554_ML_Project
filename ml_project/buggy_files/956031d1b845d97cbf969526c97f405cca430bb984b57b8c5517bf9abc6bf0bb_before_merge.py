def merge_packages_config(hass, config, packages,
                          _log_pkg_error=_log_pkg_error):
    """Merge packages into the top-level configuration. Mutate config."""
    # pylint: disable=too-many-nested-blocks
    PACKAGES_CONFIG_SCHEMA(packages)
    for pack_name, pack_conf in packages.items():
        for comp_name, comp_conf in pack_conf.items():
            if comp_name == CONF_CORE:
                continue
            component = get_component(hass, comp_name)

            if component is None:
                _log_pkg_error(pack_name, comp_name, config, "does not exist")
                continue

            if hasattr(component, 'PLATFORM_SCHEMA'):
                if not comp_conf:
                    continue  # Ensure we dont add Falsy items to list
                config[comp_name] = cv.ensure_list(config.get(comp_name))
                config[comp_name].extend(cv.ensure_list(comp_conf))
                continue

            if hasattr(component, 'CONFIG_SCHEMA'):
                merge_type, _ = _identify_config_schema(component)

                if merge_type == 'list':
                    if not comp_conf:
                        continue  # Ensure we dont add Falsy items to list
                    config[comp_name] = cv.ensure_list(config.get(comp_name))
                    config[comp_name].extend(cv.ensure_list(comp_conf))
                    continue

                if merge_type == 'dict':
                    if comp_conf is None:
                        comp_conf = OrderedDict()

                    if not isinstance(comp_conf, dict):
                        _log_pkg_error(
                            pack_name, comp_name, config,
                            "cannot be merged. Expected a dict.")
                        continue

                    if comp_name not in config:
                        config[comp_name] = OrderedDict()

                    if not isinstance(config[comp_name], dict):
                        _log_pkg_error(
                            pack_name, comp_name, config,
                            "cannot be merged. Dict expected in main config.")
                        continue

                    for key, val in comp_conf.items():
                        if key in config[comp_name]:
                            _log_pkg_error(pack_name, comp_name, config,
                                           "duplicate key '{}'".format(key))
                            continue
                        config[comp_name][key] = val
                    continue

            # The last merge type are sections that require recursive merging
            if comp_name in config:
                _recursive_merge(pack_name, comp_name, config,
                                 conf=config[comp_name], package=comp_conf)
                continue
            config[comp_name] = comp_conf

    return config