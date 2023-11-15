def validate_app_exists_in_rg(cmd, namespace):
    """Validate that the App/slot exists in the RG provided"""
    client = web_client_factory(cmd.cli_ctx)
    if isinstance(namespace.name, str) and isinstance(namespace.resource_group_name, str):
        webapp = namespace.name
        resource_group_name = namespace.resource_group_name
        if isinstance(namespace.slot, str):
            app = client.web_apps.get_slot(resource_group_name, webapp, namespace.slot, raw=True)
        else:
            app = client.web_apps.get(resource_group_name, webapp, None, raw=True)
        if app.response.status_code != 200:
            raise CLIError(app.response.text)