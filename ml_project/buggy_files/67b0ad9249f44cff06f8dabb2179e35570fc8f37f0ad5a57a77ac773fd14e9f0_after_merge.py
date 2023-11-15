def pull(
    image,
    insecure_registry=False,
    api_response=False,
    client_timeout=salt.utils.dockermod.CLIENT_TIMEOUT,
):
    """
    .. versionchanged:: 2018.3.0
        If no tag is specified in the ``image`` argument, all tags for the
        image will be pulled. For this reason is it recommended to pass
        ``image`` using the ``repo:tag`` notation.

    Pulls an image from a Docker registry

    image
        Image to be pulled

    insecure_registry : False
        If ``True``, the Docker client will permit the use of insecure
        (non-HTTPS) registries.

    api_response : False
        If ``True``, an ``API_Response`` key will be present in the return
        data, containing the raw output from the Docker API.

        .. note::

            This may result in a **lot** of additional return data, especially
            for larger images.

    client_timeout
        Timeout in seconds for the Docker client. This is not a timeout for
        this function, but for receiving a response from the API.


    **RETURN DATA**

    A dictionary will be returned, containing the following keys:

    - ``Layers`` - A dictionary containing one or more of the following keys:
        - ``Already_Pulled`` - Layers that that were already present on the
          Minion
        - ``Pulled`` - Layers that that were pulled
    - ``Status`` - A string containing a summary of the pull action (usually a
      message saying that an image was downloaded, or that it was up to date).
    - ``Time_Elapsed`` - Time in seconds taken to perform the pull


    CLI Example:

    .. code-block:: bash

        salt myminion docker.pull centos
        salt myminion docker.pull centos:6
    """
    _prep_pull()

    kwargs = {"stream": True, "client_timeout": client_timeout}
    if insecure_registry:
        kwargs["insecure_registry"] = insecure_registry

    time_started = time.time()
    response = _client_wrapper("pull", image, **kwargs)
    ret = {"Time_Elapsed": time.time() - time_started, "retcode": 0}
    _clear_context()

    if not response:
        raise CommandExecutionError(
            "Pull failed for {0}, no response returned from Docker API".format(image)
        )
    elif api_response:
        ret["API_Response"] = response

    errors = []
    # Iterate through API response and collect information
    for event in response:
        log.debug("pull event: %s", event)
        try:
            event = salt.utils.json.loads(event)
        except Exception as exc:  # pylint: disable=broad-except
            raise CommandExecutionError(
                "Unable to interpret API event: '{0}'".format(event),
                info={"Error": exc.__str__()},
            )
        try:
            event_type = next(iter(event))
        except StopIteration:
            continue
        if event_type == "status":
            _pull_status(ret, event)
        elif event_type == "errorDetail":
            _error_detail(errors, event)

    if errors:
        ret["Errors"] = errors
        ret["retcode"] = 1
    return ret