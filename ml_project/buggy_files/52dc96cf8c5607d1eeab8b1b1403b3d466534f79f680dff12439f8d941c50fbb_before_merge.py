def decrypt(click_config,

            # Other (required)
            label, message_kit,

            # API Options
            geth, provider_uri, federated_only, dev, pay_with, network, registry_filepath,
            config_file, discovery_port, hw_wallet, teacher_uri, min_stake):
    """
    Decrypt data encrypted under an Alice's policy public key.
    """
    ### Setup ###
    emitter = _setup_emitter(click_config)

    alice_config, provider_uri = _get_alice_config(click_config, config_file, dev, discovery_port, federated_only,
                                                   geth, network, pay_with, provider_uri, registry_filepath)
    #############

    ALICE = _create_alice(alice_config, click_config, dev, emitter, hw_wallet, teacher_uri, min_stake)

    # Request
    request_data = {'label': label, 'message_kit': message_kit}
    response = ALICE.controller.decrypt(request=request_data)
    return response