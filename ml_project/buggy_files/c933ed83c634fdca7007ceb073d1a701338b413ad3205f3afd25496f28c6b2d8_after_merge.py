def up(general_config, staker_options, config_file, cloudprovider, aws_profile, remote_provider, nucypher_image, seed_network, stakes, wipe, prometheus, namespace, envvars):
    """Creates workers for all stakes owned by the user for the given network."""

    emitter = setup_emitter(general_config)

    if not CloudDeployers:
        emitter.echo("Ansible is required to use this command.  (Please run 'pip install ansible'.)", color="red")
        return
    STAKEHOLDER = staker_options.create_character(emitter, config_file)

    stakers = STAKEHOLDER.get_stakers()
    if not stakers:
        emitter.echo("No staking accounts found.")
        return

    staker_addresses = filter_staker_addresses(stakers, stakes)

    config_file = config_file or StakeHolderConfiguration.default_filepath()

    deployer = CloudDeployers.get_deployer(cloudprovider)(emitter, STAKEHOLDER, config_file, remote_provider,
        nucypher_image, seed_network, aws_profile, prometheus, namespace=namespace, network=STAKEHOLDER.network, envvars=envvars)
    if staker_addresses:
        config = deployer.create_nodes(staker_addresses)

    if config.get('instances') and len(config.get('instances')) >= len(staker_addresses):
        emitter.echo('Nodes exist for all requested stakes', color="yellow")
        deployer.deploy_nucypher_on_existing_nodes(staker_addresses, wipe_nucypher=wipe)