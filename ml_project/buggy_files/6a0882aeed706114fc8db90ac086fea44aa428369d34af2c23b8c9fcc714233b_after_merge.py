def _create_ursula(ursula_config, click_config, dev, emitter, lonely, teacher_uri, min_stake, load_seednodes=True):
    #
    # Make Ursula
    #

    client_password = None
    if not ursula_config.federated_only:
        if not dev and not click_config.json_ipc:
            client_password = get_client_password(checksum_address=ursula_config.worker_address,
                                                  envvar="NUCYPHER_WORKER_ETH_PASSWORD")

    try:
        URSULA = actions.make_cli_character(character_config=ursula_config,
                                            click_config=click_config,
                                            min_stake=min_stake,
                                            teacher_uri=teacher_uri,
                                            unlock_keyring=not dev,
                                            lonely=lonely,
                                            client_password=client_password,
                                            load_preferred_teachers=load_seednodes,
                                            start_learning_now=load_seednodes)

        return URSULA
    except NucypherKeyring.AuthenticationFailed as e:
        emitter.echo(str(e), color='red', bold=True)
        # TODO: Exit codes (not only for this, but for other exceptions)
        return click.get_current_context().exit(1)