def save_metadata(click_config,

                  # API Options
                  geth, provider_uri, network, registry_filepath, staker_address, worker_address, federated_only,
                  rest_host, rest_port, db_filepath, poa, light, config_file, dev, lonely, teacher_uri, min_stake):
    """
    Manually write node metadata to disk without running.
    """
    ### Setup ###
    _validate_args(geth, federated_only, staker_address, registry_filepath)

    emitter = _setup_emitter(click_config, worker_address)

    _pre_launch_warnings(emitter, dev=dev, force=None)

    ursula_config, provider_uri = _get_ursula_config(emitter, geth, provider_uri, network, registry_filepath, dev,
                                                     config_file, staker_address, worker_address, federated_only,
                                                     rest_host, rest_port, db_filepath, poa, light)
    #############

    URSULA = _create_ursula(ursula_config, click_config, dev, emitter, lonely, teacher_uri, min_stake)

    metadata_path = URSULA.write_node_metadata(node=URSULA)
    emitter.message(f"Successfully saved node metadata to {metadata_path}.", color='green')