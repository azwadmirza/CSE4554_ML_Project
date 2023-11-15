def connect(
    runner: Runner, remote_info: RemoteInfo, is_container_mode: bool,
    expose: PortMapping
) -> Tuple[int, SSH]:
    """
    Start all the processes that handle remote proxying.

    Return (local port of SOCKS proxying tunnel, SSH instance).
    """
    span = runner.span()
    # Keep local copy of pod logs, for debugging purposes. Set is_critical to
    # False so logs failing doesn't bring down the Telepresence session.
    runner.launch(
        "kubectl logs",
        runner.kubectl(
            "logs", "-f", remote_info.pod_name, "--container",
            remote_info.container_name, "--tail=10"
        ),
        bufsize=0,
        is_critical=False,
    )

    ssh = SSH(runner, find_free_port())

    # forward remote port to here, by tunneling via remote SSH server:
    runner.launch(
        "kubectl port-forward",
        runner.kubectl(
            "port-forward", remote_info.pod_name, "{}:8022".format(ssh.port)
        )
    )

    if not ssh.wait():
        raise RuntimeError("SSH to the cluster failed to start.")

    # Create ssh tunnels. In the case of the container method, just show the
    # associated messages; the tunnels will be created in the network
    # container, where those messages are not visible to the user.
    expose_local_services(
        runner,
        ssh,
        list(expose.local_to_remote()),
        show_only=is_container_mode
    )

    # Start tunnels for the SOCKS proxy (local -> remote)
    # and the local server for the proxy to poll (remote -> local).
    socks_port = find_free_port()
    local_server_port = find_free_port()

    launch_local_server(runner, local_server_port)
    forward_args = [
        "-L127.0.0.1:{}:127.0.0.1:9050".format(socks_port),
        "-R9055:127.0.0.1:{}".format(local_server_port)
    ]
    runner.launch(
        "SSH port forward (socks and proxy poll)",
        ssh.bg_command(forward_args)
    )

    span.end()
    return socks_port, ssh