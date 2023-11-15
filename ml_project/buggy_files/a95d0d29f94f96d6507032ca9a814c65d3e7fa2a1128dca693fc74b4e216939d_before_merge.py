def run(
    name,
    image=None,
    onlyif=None,
    unless=None,
    creates=None,
    bg=False,
    failhard=True,
    replace=False,
    force=False,
    skip_translate=None,
    ignore_collisions=False,
    validate_ip_addrs=True,
    client_timeout=salt.utils.docker.CLIENT_TIMEOUT,
    **kwargs
):
    """
    .. versionadded:: 2018.3.0

    .. note::
        If no tag is specified in the image name, and nothing matching the
        specified image is pulled on the minion, the ``docker pull`` that
        retrieves the image will pull *all tags* for the image. A tag of
        ``latest`` is not implicit for the pull. For this reason, it is
        recommended to specify the image in ``repo:tag`` notation.

    Like the :py:func:`cmd.run <salt.states.cmd.run>` state, only for Docker.
    Does the equivalent of a ``docker run`` and returns information about the
    container that was created, as well as its output.

    This state accepts the same arguments as :py:func:`docker_container.running
    <salt.states.docker_container.running>`, with the exception of
    ``watch_action``, ``start``, and ``shutdown_timeout`` (though the ``force``
    argument has a different meaning in this state).

    In addition, this state accepts the arguments from :py:func:`docker.logs
    <salt.modules.dockermod.logs>`, with the exception of ``follow``, to
    control how logs are returned.

    Additionally, the following arguments are supported:

    onlyif
        A command or list of commands to run as a check. The container will
        only run if any of the specified commands returns a zero exit status.

    unless
        A command or list of commands to run as a check. The container will
        only run if any of the specified commands returns a non-zero exit
        status.

    creates
        A path or list of paths. Only run if one or more of the specified paths
        do not exist on the minion.

    bg : False
        If ``True``, run container in background and do not await or deliver
        its results.

        .. note::
            This may not be useful in cases where other states depend on the
            results of this state. Also, the logs will be inaccessible once the
            container exits if ``auto_remove`` is set to ``True``, so keep this
            in mind.

    failhard : True
        If ``True``, the state will return a ``False`` result if the exit code
        of the container is non-zero. When this argument is set to ``False``,
        the state will return a ``True`` result regardless of the container's
        exit code.

        .. note::
            This has no effect if ``bg`` is set to ``True``.

    replace : False
        If ``True``, and if the named container already exists, this will
        remove the existing container. The default behavior is to return a
        ``False`` result when the container already exists.

    force : False
        If ``True``, and the named container already exists, *and* ``replace``
        is also set to ``True``, then the container will be forcibly removed.
        Otherwise, the state will not proceed and will return a ``False``
        result.

    CLI Examples:

    .. code-block:: bash

        salt myminion docker.run_container myuser/myimage command=/usr/local/bin/myscript.sh

    **USAGE EXAMPLE**

    .. code-block:: jinja

        {% set pkg_version = salt.pillar.get('pkg_version', '1.0-1') %}
        build_package:
          docker_container.run:
            - image: myuser/builder:latest
            - binds: /home/myuser/builds:/build_dir
            - command: /scripts/build.sh {{ pkg_version }}
            - creates: /home/myuser/builds/myapp-{{ pkg_version }}.noarch.rpm
            - replace: True
            - networks:
              - mynet
            - require:
              - docker_network: mynet
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    kwargs = salt.utils.args.clean_kwargs(**kwargs)
    for unsupported in ("watch_action", "start", "shutdown_timeout", "follow"):
        if unsupported in kwargs:
            ret["result"] = False
            ret["comment"] = "The '{0}' argument is not supported".format(unsupported)
            return ret

    if image is None:
        ret["result"] = False
        ret["comment"] = "The 'image' argument is required"
        return ret
    elif not isinstance(image, six.string_types):
        image = six.text_type(image)

    cret = mod_run_check(onlyif, unless, creates)
    if isinstance(cret, dict):
        ret.update(cret)
        return ret

    try:
        if "networks" in kwargs and kwargs["networks"] is not None:
            kwargs["networks"] = _parse_networks(kwargs["networks"])
        _resolve_image(ret, image, client_timeout)
    except CommandExecutionError as exc:
        ret["result"] = False
        if exc.info is not None:
            return _format_comments(ret, exc.info)
        else:
            ret["comment"] = exc.__str__()
            return ret

    cret = mod_run_check(onlyif, unless, creates)
    if isinstance(cret, dict):
        ret.update(cret)
        return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "Container would be run{0}".format(
            " in the background" if bg else ""
        )
        return ret

    if bg:
        remove = False
    else:
        # We're doing a bit of a hack here, so that we can get the exit code after
        # the container exits. Since the input translation and compilation of the
        # host_config take place within a private function of the execution module,
        # we manually do the handling for auto_remove here and extract if (if
        # present) from the kwargs. This allows us to explicitly pass auto_remove
        # as False when we run the container, so it is still present upon exit (and
        # the exit code can be retrieved). We can then remove the container
        # manually if auto_remove is True.
        remove = None
        for item in ("auto_remove", "rm"):
            try:
                val = kwargs.pop(item)
            except KeyError:
                continue
            if remove is not None:
                if not ignore_collisions:
                    ret["result"] = False
                    ret["comment"] = (
                        "'rm' is an alias for 'auto_remove', they cannot "
                        "both be used"
                    )
                    return ret
            else:
                remove = bool(val)

        if remove is not None:
            # We popped off the value, so replace it with False
            kwargs["auto_remove"] = False
        else:
            remove = False

    try:
        ret["changes"] = __salt__["docker.run_container"](
            image,
            name=name,
            skip_translate=skip_translate,
            ignore_collisions=ignore_collisions,
            validate_ip_addrs=validate_ip_addrs,
            client_timeout=client_timeout,
            bg=bg,
            replace=replace,
            force=force,
            **kwargs
        )
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("Encountered error running container")
        ret["result"] = False
        ret["comment"] = "Encountered error running container: {0}".format(exc)
    else:
        if bg:
            ret["comment"] = "Container was run in the background"
        else:
            try:
                retcode = ret["changes"]["ExitCode"]
            except KeyError:
                pass
            else:
                ret["result"] = False if failhard and retcode != 0 else True
                ret["comment"] = (
                    "Container ran and exited with a return code of "
                    "{0}".format(retcode)
                )

    if remove:
        id_ = ret.get("changes", {}).get("Id")
        if id_:
            try:
                __salt__["docker.rm"](ret["changes"]["Id"])
            except CommandExecutionError as exc:
                ret.setdefault("warnings", []).append(
                    "Failed to auto_remove container: {0}".format(exc)
                )

    return ret