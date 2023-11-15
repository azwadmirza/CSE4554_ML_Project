def run(click_config,

        # API Options
        provider_uri, network, registry_filepath, checksum_address, dev, config_file, discovery_port,
        teacher_uri, min_stake,

        # Other
        controller_port, dry_run):
    """
    Start Bob's controller.
    """

    ### Setup ###
    emitter = _setup_emitter(click_config)

    bob_config = _get_bob_config(click_config, dev, provider_uri, network, registry_filepath, checksum_address,
                                 config_file, discovery_port)
    #############

    BOB = actions.make_cli_character(character_config=bob_config,
                                     click_config=click_config,
                                     unlock_keyring=not dev,
                                     teacher_uri=teacher_uri,
                                     min_stake=min_stake)

    # RPC
    if click_config.json_ipc:
        rpc_controller = BOB.make_rpc_controller()
        _transport = rpc_controller.make_control_transport()
        rpc_controller.start()
        return

    # Echo Public Keys
    emitter.message(f"Bob Verifying Key {bytes(BOB.stamp).hex()}", color='green', bold=True)
    bob_encrypting_key = bytes(BOB.public_keys(DecryptingPower)).hex()
    emitter.message(f"Bob Encrypting Key {bob_encrypting_key}", color="blue", bold=True)
    # Start Controller
    controller = BOB.make_web_controller(crash_on_error=click_config.debug)
    BOB.log.info('Starting HTTP Character Web Controller')
    return controller.start(http_port=controller_port, dry_run=dry_run)