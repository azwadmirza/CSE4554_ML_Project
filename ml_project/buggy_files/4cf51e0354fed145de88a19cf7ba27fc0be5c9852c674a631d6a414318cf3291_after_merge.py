def connect(
    remote_info,
    local_exposed_ports,
    expose_host,
):
    """
    Start all the processes that handle remote proxying.

    Return list of Popen instances.
    """
    processes = []
    # forward remote port to here, by tunneling via remote SSH server:
    processes.append(
        Popen(["kubectl", "port-forward", remote_info.pod_name, "22"])
    )
    wait_for_ssh()

    for port_number in local_exposed_ports:
        # XXX really only need to bind to external port...
        processes.append(
            ssh([
                "-R",
                "*:{}:{}:{}".format(port_number, expose_host, port_number)
            ])
        )

    # start tunnel to remote SOCKS proxy, for telepresence --run.
    # XXX really only need to bind to external port...
    processes.append(
        ssh(["-L", "*:{}:127.0.0.1:{}".format(SOCKS_PORT, SOCKS_PORT)])
    )

    return processes