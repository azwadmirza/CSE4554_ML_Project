def run_container(
    image,
    name=None,
    skip_translate=None,
    ignore_collisions=False,
    validate_ip_addrs=True,
    client_timeout=salt.utils.dockermod.CLIENT_TIMEOUT,
    bg=False,
    replace=False,
    force=False,
    networks=None,
    **kwargs
):
    """
    .. versionadded:: 2018.3.0

    Equivalent to ``docker run`` on the Docker CLI. Runs the container, waits
    for it to exit, and returns the container's logs when complete.

    .. note::
        Not to be confused with :py:func:`docker.run
        <salt.modules.dockermod.run>`, which provides a :py:func:`cmd.run
        <salt.modules.cmdmod.run>`-like interface for executing commands in a
        running container.

    This function accepts the same arguments as :py:func:`docker.create
    <salt.modules.dockermod.create>`, with the exception of ``start``. In
    addition, it accepts the arguments from :py:func:`docker.logs
    <salt.modules.dockermod.logs>`, with the exception of ``follow``, to
    control how logs are returned. Finally, the ``bg`` argument described below
    can be used to optionally run the container in the background (the default
    behavior is to block until the container exits).

    bg : False
        If ``True``, this function will not wait for the container to exit and
        will not return its logs. It will however return the container's name
        and ID, allowing for :py:func:`docker.logs
        <salt.modules.dockermod.logs>` to be used to view the logs.

        .. note::
            The logs will be inaccessible once the container exits if
            ``auto_remove`` is set to ``True``, so keep this in mind.

    replace : False
        If ``True``, and if the named container already exists, this will
        remove the existing container. The default behavior is to return a
        ``False`` result when the container already exists.

    force : False
        If ``True``, and the named container already exists, *and* ``replace``
        is also set to ``True``, then the container will be forcibly removed.
        Otherwise, the state will not proceed and will return a ``False``
        result.

    networks
        Networks to which the container should be connected. If automatic IP
        configuration is being used, the networks can be a simple list of
        network names. If custom IP configuration is being used, then this
        argument must be passed as a dictionary.

    CLI Examples:

    .. code-block:: bash

        salt myminion docker.run_container myuser/myimage command=/usr/local/bin/myscript.sh
        # Run container in the background
        salt myminion docker.run_container myuser/myimage command=/usr/local/bin/myscript.sh bg=True
        # Connecting to two networks using automatic IP configuration
        salt myminion docker.run_container myuser/myimage command='perl /scripts/sync.py' networks=net1,net2
        # net1 using automatic IP, net2 using static IPv4 address
        salt myminion docker.run_container myuser/myimage command='perl /scripts/sync.py' networks='{"net1": {}, "net2": {"ipv4_address": "192.168.27.12"}}'
    """
    if kwargs.pop("inspect", True) and not resolve_image_id(image):
        pull(image, client_timeout=client_timeout)

    removed_ids = None
    if name is not None:
        try:
            pre_state = __salt__["docker.state"](name)
        except CommandExecutionError:
            pass
        else:
            if pre_state == "running" and not (replace and force):
                raise CommandExecutionError(
                    "Container '{0}' exists and is running. Run with "
                    "replace=True and force=True to force removal of the "
                    "existing container.".format(name)
                )
            elif not replace:
                raise CommandExecutionError(
                    "Container '{0}' exists. Run with replace=True to "
                    "remove the existing container".format(name)
                )
            else:
                # We don't have to try/except this, we want it to raise a
                # CommandExecutionError if we fail to remove the existing
                # container so that we gracefully abort before attempting to go
                # any further.
                removed_ids = rm_(name, force=force)

    log_kwargs = {}
    for argname in get_client_args("logs")["logs"]:
        try:
            log_kwargs[argname] = kwargs.pop(argname)
        except KeyError:
            pass
    # Ignore the stream argument if passed
    log_kwargs.pop("stream", None)

    kwargs, unused_kwargs = _get_create_kwargs(
        skip_translate=skip_translate,
        ignore_collisions=ignore_collisions,
        validate_ip_addrs=validate_ip_addrs,
        **kwargs
    )

    # _get_create_kwargs() will have processed auto_remove and put it into the
    # host_config, so check the host_config to see whether or not auto_remove
    # was enabled.
    auto_remove = kwargs.get("host_config", {}).get("AutoRemove", False)

    if unused_kwargs:
        log.warning(
            "The following arguments were ignored because they are not "
            "recognized by docker-py: %s",
            sorted(unused_kwargs),
        )

    if networks:
        if isinstance(networks, six.string_types):
            networks = {x: {} for x in networks.split(",")}
        if not isinstance(networks, dict) or not all(
            isinstance(x, dict) for x in six.itervalues(networks)
        ):
            raise SaltInvocationError("Invalid format for networks argument")

    log.debug(
        "docker.create: creating container %susing the following " "arguments: %s",
        "with name '{0}' ".format(name) if name is not None else "",
        kwargs,
    )

    time_started = time.time()
    # Create the container
    ret = _client_wrapper("create_container", image, name=name, **kwargs)

    if removed_ids:
        ret["Replaces"] = removed_ids

    if name is None:
        name = inspect_container(ret["Id"])["Name"].lstrip("/")
    ret["Name"] = name

    def _append_warning(ret, msg):
        warnings = ret.pop("Warnings", None)
        if warnings is None:
            warnings = [msg]
        elif isinstance(ret, list):
            warnings.append(msg)
        else:
            warnings = [warnings, msg]
        ret["Warnings"] = warnings

    exc_info = {"return": ret}
    try:
        if networks:
            try:
                for net_name, net_conf in six.iteritems(networks):
                    __salt__["docker.connect_container_to_network"](
                        ret["Id"], net_name, **net_conf
                    )
            except CommandExecutionError as exc:
                # Make an effort to remove the container if auto_remove was enabled
                if auto_remove:
                    try:
                        rm_(name)
                    except CommandExecutionError as rm_exc:
                        exc_info.setdefault("other_errors", []).append(
                            "Failed to auto_remove container: {0}".format(rm_exc)
                        )
                # Raise original exception with additonal info
                raise CommandExecutionError(exc.__str__(), info=exc_info)

        # Start the container
        output = []
        start_(ret["Id"])
        if not bg:
            # Can't use logs() here because we've disabled "stream" in that
            # function.  Also, note that if you want to troubleshoot this for loop
            # in a debugger like pdb or pudb, you'll want to use auto_remove=False
            # when running the function, since the container will likely exit
            # before you finish stepping through with a debugger. If the container
            # exits during iteration, the next iteration of the generator will
            # raise an exception since the container will no longer exist.
            try:
                for line in _client_wrapper(
                    "logs", ret["Id"], stream=True, timestamps=False
                ):
                    output.append(salt.utils.stringutils.to_unicode(line))
            except CommandExecutionError:
                msg = (
                    "Failed to get logs from container. This may be because "
                    "the container exited before Salt was able to attach to "
                    "it to retrieve the logs. Consider setting auto_remove "
                    "to False."
                )
                _append_warning(ret, msg)
        # Container has exited, note the elapsed time
        ret["Time_Elapsed"] = time.time() - time_started
        _clear_context()

        if not bg:
            ret["Logs"] = "".join(output)
            if not auto_remove:
                try:
                    cinfo = inspect_container(ret["Id"])
                except CommandExecutionError:
                    _append_warning(ret, "Failed to inspect container after running")
                else:
                    cstate = cinfo.get("State", {})
                    cstatus = cstate.get("Status")
                    if cstatus != "exited":
                        _append_warning(ret, "Container state is not 'exited'")
                    ret["ExitCode"] = cstate.get("ExitCode")

    except CommandExecutionError as exc:
        try:
            exc_info.update(exc.info)
        except (TypeError, ValueError):
            # In the event exc.info wasn't a dict (extremely unlikely), append
            # it to other_errors as a fallback.
            exc_info.setdefault("other_errors", []).append(exc.info)
        # Re-raise with all of the available additional info
        raise CommandExecutionError(exc.__str__(), info=exc_info)

    return ret