def get_env_variables(remote_info):
    """
    Generate environment variables that match kubernetes.
    """
    remote_env = remote_info.pod_environment
    deployment_set_keys = get_deployment_set_keys(remote_info)
    service_names = remote_info.service_names
    # Tell local process about the remote setup, useful for testing and
    # debugging:
    socks_result = {
        "TELEPRESENCE_POD": remote_info.pod_name,
        "TELEPRESENCE_CONTAINER": remote_info.container_name
    }
    # ips proxied via socks, can copy addresses unmodified:
    for key, value in remote_env.items():
        if key in deployment_set_keys:
            # Copy over Deployment-set env variables:
            socks_result[key] = value
        for service_name in service_names:
            # Copy over Service env variables to SOCKS variant:
            if key.startswith(service_name + "_") and (
                key.endswith("_ADDR") or key.endswith("_PORT") or
                key.endswith("_PROTO") or key.endswith("_HOST") or
                key.endswith("_TCP")
            ):
                socks_result[key] = value
    return socks_result