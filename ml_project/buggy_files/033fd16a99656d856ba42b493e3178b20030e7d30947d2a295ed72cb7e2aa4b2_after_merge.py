def stop(name, timeout=None, **kwargs):
    """
    Stops a running container

    name
        Container name or ID

    unpause : False
        If ``True`` and the container is paused, it will be unpaused before
        attempting to stop the container.

    timeout
        Timeout in seconds after which the container will be killed (if it has
        not yet gracefully shut down)

        .. versionchanged:: 2017.7.0
            If this argument is not passed, then the container's configuration
            will be checked. If the container was created using the
            ``stop_timeout`` argument, then the configured timeout will be
            used, otherwise the timeout will be 10 seconds.

    **RETURN DATA**

    A dictionary will be returned, containing the following keys:

    - ``status`` - A dictionary showing the prior state of the container as
      well as the new state
    - ``result`` - A boolean noting whether or not the action was successful
    - ``comment`` - Only present if the container can not be stopped


    CLI Examples:

    .. code-block:: bash

        salt myminion docker.stop mycontainer
        salt myminion docker.stop mycontainer unpause=True
        salt myminion docker.stop mycontainer timeout=20
    """
    if timeout is None:
        try:
            # Get timeout from container config
            timeout = inspect_container(name)["Config"]["StopTimeout"]
        except KeyError:
            # Fall back to a global default defined in salt.utils.dockermod
            timeout = salt.utils.dockermod.SHUTDOWN_TIMEOUT

    orig_state = state(name)
    if orig_state == "paused":
        if kwargs.get("unpause", False):
            unpause_result = _change_state(name, "unpause", "running")
            if unpause_result["result"] is False:
                unpause_result["comment"] = "Failed to unpause container '{0}'".format(
                    name
                )
                return unpause_result
        else:
            return {
                "result": False,
                "state": {"old": orig_state, "new": orig_state},
                "comment": (
                    "Container '{0}' is paused, run with "
                    "unpause=True to unpause before stopping".format(name)
                ),
            }
    ret = _change_state(name, "stop", "stopped", timeout=timeout)
    ret["state"]["old"] = orig_state
    return ret