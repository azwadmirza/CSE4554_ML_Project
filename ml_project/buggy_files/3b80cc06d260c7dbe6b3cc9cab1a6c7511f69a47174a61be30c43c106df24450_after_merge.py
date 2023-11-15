def deploy(general_config, remote_provider, nucypher_image, seed_network, wipe, prometheus, namespace, network, gas_strategy, include_hosts, envvars):
    """Deploys NuCypher on managed hosts."""

    emitter = setup_emitter(general_config)

    if not CloudDeployers:
        emitter.echo("Ansible is required to use `nucypher cloudworkers *` commands.  (Please run 'pip install ansible'.)", color="red")
        return

    deployer = CloudDeployers.get_deployer('generic')(emitter, None, None, remote_provider, nucypher_image, seed_network,
        prometheus=prometheus, namespace=namespace, network=network, gas_strategy=gas_strategy, envvars=envvars)

    hostnames = deployer.config['instances'].keys()
    if include_hosts:
        hostnames = include_hosts
    for name, hostdata in [(n, d) for n, d in deployer.config['instances'].items() if n in hostnames]:
        emitter.echo(f'\t{name}: {hostdata["publicaddress"]}', color="yellow")
    deployer.deploy_nucypher_on_existing_nodes(hostnames, wipe_nucypher=wipe)