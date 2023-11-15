def create(general_config, cloudprovider, aws_profile, remote_provider, nucypher_image, seed_network, prometheus, count, namespace, network, envvars):
    """Creates the required number of workers to be staked later under a namespace"""

    emitter = setup_emitter(general_config)

    if not CloudDeployers:
        emitter.echo("Ansible is required to use this command.  (Please run 'pip install ansible'.)", color="red")
        return

    deployer = CloudDeployers.get_deployer(cloudprovider)(emitter, None, None, remote_provider, nucypher_image, seed_network,
        aws_profile, prometheus, namespace=namespace, network=network, envvars=envvars)

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