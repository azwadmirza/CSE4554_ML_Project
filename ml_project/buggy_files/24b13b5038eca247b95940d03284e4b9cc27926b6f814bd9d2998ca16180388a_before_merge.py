def main(
    uid, deployment_name, local_exposed_ports, custom_proxied_hosts,
    expose_host
):
    processes = []
    remote_info = get_remote_info(deployment_name)
    # Wait for pod to be running:
    wait_for_pod(remote_info)
    proxied_ports = set(range(2000, 2020)) | set(map(int, local_exposed_ports))
    proxied_ports.add(22)
    proxied_ports.add(SOCKS_PORT)
    custom_ports = [int(s.split(":", 1)[1]) for s in custom_proxied_hosts]
    for port in custom_ports:
        if port in proxied_ports:
            exit((
                "OOPS: Can't proxy port {} more than once. "
                "Currently mapped ports: {}.This error is due "
                "to a limitation in Telepresence, see "
                "https://github.com/datawire/telepresence/issues/6"
            ).format(port, proxied_ports))
        else:
            proxied_ports.add(int(port))

    # write /etc/hosts
    write_etc_hosts([s.split(":", 1)[0] for s in custom_proxied_hosts])

    processes = connect(
        remote_info, local_exposed_ports, expose_host, custom_proxied_hosts
    )

    # write docker envfile, which tells CLI we're ready:
    time.sleep(5)
    write_env(remote_info, uid)

    # Now, poll processes; if one dies kill them all and restart them:
    while True:
        for p in processes:
            code = p.poll()
            if code is not None:
                print("A subprocess died, killing all processes...")
                killall(processes)
                # Unfortunatly torsocks doesn't deal well with connections
                # being lost, so best we can do is shut down.
                raise SystemExit(3)