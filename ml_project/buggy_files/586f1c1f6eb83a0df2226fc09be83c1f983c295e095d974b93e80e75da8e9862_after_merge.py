def first_login(client: GMatrixClient, signer: Signer, username: str, cap_str: str) -> User:
    """Login within a server.

    There are multiple cases where a previous auth token can become invalid and
    a new login is necessary:

    - The server is configured to automatically invalidate tokens after a while
      (not the default)
    - A server operator may manually wipe or invalidate existing access tokens
    - A node may have roamed to a different server (e.g. because the original
      server was temporarily unavailable) and is now 'returning' to the
      previously used server.

    This relies on the Matrix server having the `eth_auth_provider` plugin
    installed, the plugin will automatically create the user on the first
    login. The plugin requires the password to be the signature of the server
    hostname, verified by the server to prevent account creation spam.

    Displayname is the signature of the whole user_id (including homeserver),
    to be verified by other peers and prevent impersonation attacks.
    """
    server_url = client.api.base_url
    server_name = urlparse(server_url).netloc

    # The plugin `eth_auth_provider` expects a signature of the server_name as
    # the user's password.
    #
    # For a honest matrix server:
    #
    # - This prevents impersonation attacks / name squatting, since the plugin
    # will validate the username by recovering the address from the signature
    # and check the recovered address and the username matches.
    #
    # For a badly configured server (one without the plugin):
    #
    # - An attacker can front run and register the username before the honest
    # user:
    #    - Because the attacker cannot guess the correct password, when the
    #    honest node tries to login it will fail, which tells us the server is
    #    improperly configured and should be blacklisted.
    #    - The attacker cannot forge a signature to use as a display name, so
    #    the partner node can tell there is a malicious node trying to
    #    eavesdrop the conversation and that matrix server should be
    #    blacklisted.
    # - The username is available, but because the plugin is not installed the
    # login will fail since the user is not registered. Here too one can infer
    # the server is improperly configured and blacklist the server.
    password = encode_hex(signer.sign(server_name.encode()))

    # Disabling sync because login is done before the transport is fully
    # initialized, i.e. the inventory rooms don't have the callbacks installed.
    client.login(username, password, sync=False, device_id="raiden")

    # Because this is the first login, the display name has to be set, this
    # prevents the impersonation mentioned above. subsequent calls will reuse
    # the authentication token and the display name will be properly set.
    signature_bytes = signer.sign(client.user_id.encode())
    signature_hex = encode_hex(signature_bytes)

    user = client.get_user(client.user_id)

    try:
        current_display_name = user.get_display_name()
    except MatrixRequestError as ex:
        # calling site
        log.error(
            "Ignoring Matrix error in `get_display_name`",
            exc_info=ex,
            user_id=user.user_id,
        )
        current_display_name = ""

    # Only set the display name if necessary, since this is a slow operation.
    if current_display_name != signature_hex:
        user.set_display_name(signature_hex)

    try:
        current_capabilities = user.get_avatar_url() or ""
    except MatrixRequestError as ex:
        log.error(
            "Ignoring Matrix error in `get_avatar_url`",
            exc_info=ex,
            user_id=user.user_id,
        )
        current_capabilities = ""

    # Only set the capabilities if necessary.
    if current_capabilities != cap_str:
        user.set_avatar_url(cap_str)

    log.debug(
        "Logged in",
        node=to_checksum_address(username),
        homeserver=server_name,
        server_url=server_url,
    )
    return user