def add(general_config, host_address, login_name, key_path, ssh_port, host_nickname, namespace, network):
    """Adds an existing node to the local config for future management."""

    emitter = setup_emitter(general_config)
    name = host_nickname

    deployer = CloudDeployers.get_deployer('generic')(emitter, None, None, namespace=namespace, network=network, action='add')
    config = deployer.create_nodes([name], host_address, login_name, key_path, ssh_port)
    emitter.echo(f'Success.  Now run `nucypher cloudworkers deploy --namespace {namespace} --remote-provider <an eth provider>` to deploy Nucypher on this node.', color='green')