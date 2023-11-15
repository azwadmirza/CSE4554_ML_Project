def reload_data_managers(app, **kwargs):
    from galaxy.tools.data_manager.manager import DataManagers
    log.debug("Executing data managers reload on '%s'", app.config.server_name)
    app._configure_tool_data_tables(from_shed_config=False)
    reload_tool_data_tables(app)
    reload_count = app.data_managers._reload_count
    app.data_managers = DataManagers(app, conf_watchers=app.data_managers.conf_watchers)
    app.data_managers._reload_count = reload_count + 1