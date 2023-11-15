def _convert_to_airflow_pod(pod):
    """
    Converts a k8s V1Pod object into an `airflow.kubernetes.pod.Pod` object.
    This function is purely for backwards compatibility
    """
    base_container = pod.spec.containers[0]  # type: k8s.V1Container
    env_vars, secrets = _extract_env_vars_and_secrets(base_container.env)
    volumes = _extract_volumes(pod.spec.volumes)
    api_client = ApiClient()
    init_containers = pod.spec.init_containers
    image_pull_secrets = pod.spec.image_pull_secrets or []
    if pod.spec.init_containers is not None:
        init_containers = [api_client.sanitize_for_serialization(i) for i in pod.spec.init_containers]
    dummy_pod = Pod(
        image=base_container.image,
        envs=env_vars,
        cmds=base_container.command,
        args=base_container.args,
        labels=pod.metadata.labels,
        annotations=pod.metadata.annotations,
        node_selectors=pod.spec.node_selector,
        name=pod.metadata.name,
        ports=_extract_ports(base_container.ports),
        volumes=volumes,
        volume_mounts=_extract_volume_mounts(base_container.volume_mounts),
        namespace=pod.metadata.namespace,
        image_pull_policy=base_container.image_pull_policy or 'IfNotPresent',
        tolerations=pod.spec.tolerations,
        init_containers=init_containers,
        image_pull_secrets=",".join([i.name for i in image_pull_secrets]),
        resources=base_container.resources,
        service_account_name=pod.spec.service_account_name,
        secrets=secrets,
        affinity=api_client.sanitize_for_serialization(pod.spec.affinity),
        hostnetwork=pod.spec.host_network,
        security_context=_extract_security_context(pod.spec.security_context)
    )
    return dummy_pod