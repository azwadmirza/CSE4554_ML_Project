def _get_create_kwargs(
    skip_translate=None,
    ignore_collisions=False,
    validate_ip_addrs=True,
    client_args=None,
    **kwargs
):
    """
    Take input kwargs and return a kwargs dict to pass to docker-py's
    create_container() function.
    """

    networks = kwargs.pop("networks", {})
    if kwargs.get("network_mode", "") in networks:
        networks = {kwargs["network_mode"]: networks[kwargs["network_mode"]]}
    else:
        networks = {}

    kwargs = __utils__["docker.translate_input"](
        salt.utils.dockermod.translate.container,
        skip_translate=skip_translate,
        ignore_collisions=ignore_collisions,
        validate_ip_addrs=validate_ip_addrs,
        **__utils__["args.clean_kwargs"](**kwargs)
    )

    if networks:
        kwargs["networking_config"] = _create_networking_config(networks)

    if client_args is None:
        try:
            client_args = get_client_args(["create_container", "host_config"])
        except CommandExecutionError as exc:
            log.error(
                "docker.create: Error getting client args: '%s'",
                exc.__str__(),
                exc_info=True,
            )
            raise CommandExecutionError("Failed to get client args: {0}".format(exc))

    full_host_config = {}
    host_kwargs = {}
    create_kwargs = {}
    # Using list() becausee we'll be altering kwargs during iteration
    for arg in list(kwargs):
        if arg in client_args["host_config"]:
            host_kwargs[arg] = kwargs.pop(arg)
            continue
        if arg in client_args["create_container"]:
            if arg == "host_config":
                full_host_config.update(kwargs.pop(arg))
            else:
                create_kwargs[arg] = kwargs.pop(arg)
            continue
    create_kwargs["host_config"] = _client_wrapper("create_host_config", **host_kwargs)
    # In the event that a full host_config was passed, overlay it on top of the
    # one we just created.
    create_kwargs["host_config"].update(full_host_config)
    # The "kwargs" dict at this point will only contain unused args
    return create_kwargs, kwargs