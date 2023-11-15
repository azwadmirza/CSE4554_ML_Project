def derive_policy_pubkey(click_config,

                         # Other (required)
                         label,

                         # API Options
                         geth, provider_uri, federated_only, dev, pay_with, network, registry_filepath,
                         config_file, discovery_port, hw_wallet, teacher_uri, min_stake):
    """
    Get a policy public key from a policy label.
    """
    ### Setup ###
    emitter = _setup_emitter(click_config)

    alice_config, provider_uri = _get_alice_config(click_config, config_file, dev, discovery_port, federated_only,
                                                   geth, network, pay_with, provider_uri, registry_filepath)
    #############

    ALICE = _create_alice(alice_config, click_config, dev,
                          emitter, hw_wallet, teacher_uri, min_stake, load_seednodes=False)

    # Request
    return ALICE.controller.derive_policy_encrypting_key(label=label)