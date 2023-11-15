def get_env_variables(remote_info):
    """
    Generate environment variables that match kubernetes.

    For both Docker and non-Docker we copy environment variables explicitly set
    in the Deployment template.

    For Docker we make modified versions of the Servic env variables. For
    non-Docker (SOCKS) we just copy the Service env variables as is.
    """
    remote_env = get_remote_env(remote_info)
    deployment_set_keys = get_deployment_set_keys(remote_info)
    service_names = _get_service_names(remote_env)
    # ips proxied via docker, so need to modify addresses:
    in_docker_result = {}
    # XXX we're recreating the port generation logic
    i = 0
    for i, name in enumerate(service_names):
        port = str(2000 + i)
        ip = "127.0.0.1"
        # XXX will be wrong for UDP
        full_address = "tcp://{}:{}".format(ip, port)
        in_docker_result[name + "_SERVICE_HOST"] = ip
        in_docker_result[name + "_SERVICE_PORT"] = port
        in_docker_result[name + "_PORT"] = full_address
        port_name = name + "_PORT_" + port + "_TCP"
        in_docker_result[port_name] = full_address
        # XXX will break for UDP
        in_docker_result[port_name + "_PROTO"] = "tcp"
        in_docker_result[port_name + "_PORT"] = port
        in_docker_result[port_name + "_ADDR"] = ip
    socks_result = {}
    for key, value in remote_env.items():
        if key in deployment_set_keys:
            # Copy over Deployment-set env variables:
            in_docker_result[key] = value
            socks_result[key] = value
        for service_name in service_names:
            # Copy over Service env variables to SOCKS variant:
            if key.startswith(service_name + "_") and (
                key.endswith("_ADDR") or key.endswith("_PORT") or
                key.endswith("_PROTO") or key.endswith("_HOST") or
                key.endswith("_TCP")
            ):
                socks_result[key] = value
    # Tell local process about the remote setup, useful for testing and
    # debugging:
    socks_result["TELEPRESENCE_POD"] = remote_info.pod_name
    socks_result["TELEPRESENCE_CONTAINER"] = remote_info.container_name
    return in_docker_result, socks_result