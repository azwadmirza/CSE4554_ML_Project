def public_keys(click_config,

                # API Options
                provider_uri, network, registry_filepath, checksum_address, dev, config_file, discovery_port,
                teacher_uri, min_stake):
    """
    Obtain Bob's public verification and encryption keys.
    """

    ### Setup ###
    _setup_emitter(click_config)

    bob_config = _get_bob_config(click_config, dev, provider_uri, network, registry_filepath, checksum_address,
                                 config_file, discovery_port)
    #############

    BOB = actions.make_cli_character(character_config=bob_config,
                                     click_config=click_config,
                                     dev=dev,
                                     teacher_uri=teacher_uri,
                                     min_stake=min_stake)

    response = BOB.controller.public_keys()
    return response