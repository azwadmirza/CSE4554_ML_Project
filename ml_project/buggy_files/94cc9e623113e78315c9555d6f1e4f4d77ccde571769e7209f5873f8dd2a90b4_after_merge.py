def register_plugin(plugin):
    existing = SERVICE_PLUGINS.get(plugin.name())
    if existing:
        if existing.priority > plugin.priority:
            return
    SERVICE_PLUGINS[plugin.name()] = plugin