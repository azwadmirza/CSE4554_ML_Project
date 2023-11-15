def connect(
    remote_info, local_exposed_ports, expose_host, custom_proxied_hosts
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
        processes.append(
            ssh([
                "-R",
                "*:{}:{}:{}".format(port_number, expose_host, port_number)
            ])
        )

    # start tunnel to remote SOCKS proxy, for telepresence --run:
    processes.append(
        ssh(["-L", "*:{}:127.0.0.1:{}".format(SOCKS_PORT, SOCKS_PORT)])
    )

    # start proxies for custom-mapped hosts:
    for host, port in [s.split(":", 1) for s in custom_proxied_hosts]:
        processes.append(ssh(["-L", "{}:{}:{}".format(port, host, port)]))

    # start proxies for Services:
    # XXX maybe just do everything via SSH, now that we have it?
    for port in range(2000, 2020):
        # XXX what if there is more than 20 services
        p = Popen(["kubectl", "port-forward", remote_info.pod_name, str(port)])
        processes.append(p)

    return processes