def update(general_config, remote_provider, nucypher_image, seed_network, sentry_dsn, wipe, prometheus, namespace, network, gas_strategy, include_hosts):
    """Updates existing installations of Nucypher on existing managed remote hosts."""

    emitter = setup_emitter(general_config)

    if not CloudDeployers:
        emitter.echo("Ansible is required to use `nucypher cloudworkers *` commands.  (Please run 'pip install ansible'.)", color="red")
        return

    deployer = CloudDeployers.get_deployer('generic')(
        emitter, None, None, remote_provider, nucypher_image,
        seed_network, sentry_dsn,
        prometheus=prometheus, namespace=namespace, network=network, gas_strategy=gas_strategy
    )

    emitter.echo(f"found deploying {nucypher_image} on the following existing hosts:")

    hostnames = deployer.config['instances'].keys()
    if include_hosts:
        hostnames = include_hosts
    for name, hostdata in [(n, d) for n, d in deployer.config['instances'].items() if n in hostnames]:
        emitter.echo(f'\t{name}: {hostdata["publicaddress"]}', color="yellow")
    deployer.update_nucypher_on_existing_nodes(hostnames)