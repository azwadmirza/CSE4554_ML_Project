def public_keys(click_config,

                # API Options
                geth, provider_uri, federated_only, dev, pay_with, network, registry_filepath,
                config_file, discovery_port, hw_wallet, teacher_uri, min_stake):
    """
    Obtain Alice's public verification and encryption keys.
    """

    ### Setup ###
    emitter = _setup_emitter(click_config)
    alice_config, provider_uri = _get_alice_config(click_config, config_file, dev, discovery_port, federated_only,
                                                   geth, network, pay_with, provider_uri, registry_filepath)
    #############

    ALICE = _create_alice(alice_config, click_config, dev,
                          emitter, hw_wallet, teacher_uri, min_stake, load_seednodes=False)

    response = ALICE.controller.public_keys()
    return response