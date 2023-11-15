def load_entrypoint_plugins(entry_points, airflow_plugins):
    """
    Load AirflowPlugin subclasses from the entrypoints
    provided. The entry_point group should be 'airflow.plugins'.

    :param entry_points: A collection of entrypoints to search for plugins
    :type entry_points: Generator[setuptools.EntryPoint, None, None]
    :param airflow_plugins: A collection of existing airflow plugins to
        ensure we don't load duplicates
    :type airflow_plugins: list[type[airflow.plugins_manager.AirflowPlugin]]
    :rtype: list[airflow.plugins_manager.AirflowPlugin]
    """
    global import_errors  # pylint: disable=global-statement
    for entry_point, dist in entry_points:
        log.debug('Importing entry_point plugin %s', entry_point.name)
        try:
            plugin_obj = entry_point.load()
            plugin_obj.__usable_import_name = entry_point.module
            if not is_valid_plugin(plugin_obj, airflow_plugins):
                continue

            if callable(getattr(plugin_obj, 'on_load', None)):
                plugin_obj.on_load()

                airflow_plugins.append(plugin_obj)
        except Exception as e:  # pylint: disable=broad-except
            log.exception("Failed to import plugin %s", entry_point.name)
            import_errors[entry_point.module] = str(e)
    return airflow_plugins