def main(uid, deployment_name, local_exposed_ports, expose_host):
    remote_info = get_remote_info(deployment_name)

    processes = connect(
        remote_info,
        local_exposed_ports,
        expose_host,
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