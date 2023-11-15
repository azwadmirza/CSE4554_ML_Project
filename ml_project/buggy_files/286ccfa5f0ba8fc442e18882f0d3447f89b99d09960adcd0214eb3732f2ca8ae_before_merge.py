def create(general_config, cloudprovider, aws_profile, remote_provider, nucypher_image, seed_network, sentry_dsn, prometheus, count, namespace, network):
    """Creates the required number of workers to be staked later under a namespace"""

    emitter = setup_emitter(general_config)

    if not CloudDeployers:
        emitter.echo("Ansible is required to use this command.  (Please run 'pip install ansible'.)", color="red")
        return

    deployer = CloudDeployers.get_deployer(cloudprovider)(emitter, None, None, remote_provider, nucypher_image, seed_network, sentry_dsn, aws_profile, prometheus, namespace=namespace, network=network)
    if not namespace:
        emitter.echo("A namespace is required. Choose something to help differentiate between hosts, such as their specific purpose, or even just today's date.", color="red")
        return

    names = []
    i = 1
    while len(names) < count:
        name = f'{namespace}-{network}-{i}'
        if name not in deployer.config.get('instances', {}):
            names.append(name)
        i += 1
    config = deployer.create_nodes(names, unstaked=True)

    if config.get('instances') and len(config.get('instances')) >= count:
        emitter.echo('The requested number of nodes now exist', color="green")
        deployer.deploy_nucypher_on_existing_nodes(names)