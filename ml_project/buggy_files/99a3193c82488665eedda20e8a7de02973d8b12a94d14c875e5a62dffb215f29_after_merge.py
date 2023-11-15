def config(general_config, config_options, config_file):
    """View and optionally update the Ursula node's configuration."""
    emitter = setup_emitter(general_config, config_options.worker_address)
    if not config_file:
        config_file = select_config_file(emitter=emitter,
                                         checksum_address=config_options.worker_address,
                                         config_class=UrsulaConfiguration)
    updates = config_options.get_updates()
    get_or_update_configuration(emitter=emitter,
                                config_class=UrsulaConfiguration,
                                filepath=config_file,
                                updates=updates)