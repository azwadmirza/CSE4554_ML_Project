def _get_credentials(cli_ctx,
                     registry_name,
                     resource_group_name,
                     username,
                     password,
                     only_refresh_token,
                     repository=None,
                     permission='*'):
    """Try to get AAD authorization tokens or admin user credentials.
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    :param str username: The username used to log into the container registry
    :param str password: The password used to log into the container registry
    :param bool only_refresh_token: Whether to ask for only refresh token, or for both refresh and access tokens
    :param str repository: Repository for which the access token is requested
    :param str permission: The requested permission on the repository, '*' or 'pull'
    """
    registry, _ = get_registry_by_name(cli_ctx, registry_name, resource_group_name)
    login_server = registry.login_server

    # 1. if username was specified, verify that password was also specified
    if username:
        if not password:
            try:
                password = prompt_pass(msg='Password: ')
            except NoTTYException:
                raise CLIError('Please specify both username and password in non-interactive mode.')

        return login_server, username, password

    # 2. if we don't yet have credentials, attempt to get a refresh token
    if not password and registry.sku.name in MANAGED_REGISTRY_SKU:
        try:
            username = "00000000-0000-0000-0000-000000000000" if only_refresh_token else None
            password = _get_aad_token(login_server, only_refresh_token, repository, permission)
            return login_server, username, password
        except CLIError as e:
            logger.warning("Unable to get AAD authorization tokens with message: %s", str(e))

    # 3. if we still don't have credentials, attempt to get the admin credentials (if enabled)
    if not password:
        try:
            client = cf_acr_registries(cli_ctx)
            cred = get_acr_credentials(cli_ctx, client, registry_name)
            username = cred.username
            password = cred.passwords[0].value
            return login_server, username, password
        except CLIError as e:
            logger.warning("Unable to get admin user credentials with message: %s", str(e))

    # 4. if we still don't have credentials, prompt the user
    if not password:
        try:
            username = prompt('Username: ')
            password = prompt_pass(msg='Password: ')
            return login_server, username, password
        except NoTTYException:
            raise CLIError(
                'Unable to authenticate using AAD or admin login credentials. ' +
                'Please specify both username and password in non-interactive mode.')