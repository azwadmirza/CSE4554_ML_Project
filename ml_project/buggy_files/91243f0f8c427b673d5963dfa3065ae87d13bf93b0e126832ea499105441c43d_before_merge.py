def _check_registry_health(cmd, registry_name, ignore_errors):
    if registry_name is None:
        logger.warning("Registry name must be provided to check connectivity.")
        return

    # Connectivity
    try:
        registry, _ = get_registry_by_name(cmd.cli_ctx, registry_name)
        login_server = registry.login_server.rstrip('/')
    except CLIError:
        from ._docker_utils import get_login_server_suffix
        suffix = get_login_server_suffix(cmd.cli_ctx)

        if not suffix:
            from ._errors import LOGIN_SERVER_ERROR
            _handle_error(LOGIN_SERVER_ERROR.format_error_message(registry_name), ignore_errors)
            return

        login_server = registry_name + suffix

    status_validated = _get_registry_status(login_server, registry_name, ignore_errors)
    if status_validated:
        _get_endpoint_and_token_status(cmd, login_server, ignore_errors)

    # CMK settings
    if registry.encryption and registry.encryption.key_vault_properties:  # pylint: disable=too-many-nested-blocks
        client_id = registry.encryption.key_vault_properties.identity
        valid_identity = False
        if registry.identity:
            valid_identity = (client_id == 'system') and bool(registry.identity.principal_id)  # use system identity?
            if not valid_identity and registry.identity.user_assigned_identities:
                for k, v in registry.identity.user_assigned_identities.items():
                    if v.client_id == client_id:
                        from msrestazure.azure_exceptions import CloudError
                        try:
                            valid_identity = (resolve_identity_client_id(cmd.cli_ctx, k) == client_id)
                        except CloudError:
                            pass
        if not valid_identity:
            from ._errors import CMK_MANAGED_IDENTITY_ERROR
            _handle_error(CMK_MANAGED_IDENTITY_ERROR.format_error_message(registry_name), ignore_errors)