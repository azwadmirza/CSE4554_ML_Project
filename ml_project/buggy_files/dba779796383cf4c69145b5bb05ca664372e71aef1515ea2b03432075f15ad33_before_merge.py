def _create_alice(alice_config, click_config, dev, emitter, hw_wallet, teacher_uri, min_stake):
    #
    # Produce Alice
    #
    client_password = None
    if not alice_config.federated_only:
        if (not hw_wallet or not dev) and not click_config.json_ipc:
            client_password = get_client_password(checksum_address=alice_config.checksum_address)
    try:
        ALICE = actions.make_cli_character(character_config=alice_config,
                                           click_config=click_config,
                                           dev=dev,
                                           teacher_uri=teacher_uri,
                                           min_stake=min_stake,
                                           client_password=client_password)

        return ALICE
    except NucypherKeyring.AuthenticationFailed as e:
        emitter.echo(str(e), color='red', bold=True)
        click.get_current_context().exit(1)