def add_for_stake(general_config, staker_options, config_file, staker_address, host_address, login_name, key_path, ssh_port, namespace):
    """Sets an existing node as the host for the given staker address."""

    emitter = setup_emitter(general_config)

    STAKEHOLDER = staker_options.create_character(emitter, config_file)

    stakers = STAKEHOLDER.get_stakers()
    if not stakers:
        emitter.echo("No staking accounts found.")
        return

    staker_addresses = filter_staker_addresses(stakers, [staker_address])
    if not staker_addresses:
        emitter.echo(f"Could not find staker address: {staker_address} among your stakes. (try `nucypher stake --list`)", color="red")
        return

    config_file = config_file or StakeHolderConfiguration.default_filepath()

    deployer = CloudDeployers.get_deployer('generic')(emitter, STAKEHOLDER, config_file, namespace=namespace, network=STAKEHOLDER.network, action='add_for_stake')
    config = deployer.create_nodes(staker_addresses, host_address, login_name, key_path, ssh_port)