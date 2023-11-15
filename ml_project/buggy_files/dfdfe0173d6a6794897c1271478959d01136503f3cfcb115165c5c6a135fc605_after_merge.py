def push(
    image,
    insecure_registry=False,
    api_response=False,
    client_timeout=salt.utils.dockermod.CLIENT_TIMEOUT,
):
    """
    .. versionchanged:: 2015.8.4
        The ``Id`` and ``Image`` keys are no longer present in the return data.
        This is due to changes in the Docker Remote API.

    Pushes an image to a Docker registry. See the documentation at top of this
    page to configure authentication credentials.

    image
        Image to be pushed. If just the repository name is passed, then all
        tagged images for the specified repo will be pushed. If the image name
        is passed in ``repo:tag`` notation, only the specified image will be
        pushed.

    insecure_registry : False
        If ``True``, the Docker client will permit the use of insecure
        (non-HTTPS) registries.

    api_response : False
        If ``True``, an ``API_Response`` key will be present in the return
        data, containing the raw output from the Docker API.

    client_timeout
        Timeout in seconds for the Docker client. This is not a timeout for
        this function, but for receiving a response from the API.


    **RETURN DATA**

    A dictionary will be returned, containing the following keys:

    - ``Layers`` - A dictionary containing one or more of the following keys:
        - ``Already_Pushed`` - Layers that that were already present on the
          Minion
        - ``Pushed`` - Layers that that were pushed
    - ``Time_Elapsed`` - Time in seconds taken to perform the push


    CLI Example:

    .. code-block:: bash

        salt myminion docker.push myuser/mycontainer
        salt myminion docker.push myuser/mycontainer:mytag
    """
    if not isinstance(image, six.string_types):
        image = six.text_type(image)

    kwargs = {"stream": True, "client_timeout": client_timeout}
    if insecure_registry:
        kwargs["insecure_registry"] = insecure_registry

    time_started = time.time()
    response = _client_wrapper("push", image, **kwargs)
    ret = {"Time_Elapsed": time.time() - time_started, "retcode": 0}
    _clear_context()

    if not response:
        raise CommandExecutionError(
            "Push failed for {0}, no response returned from Docker API".format(image)
        )
    elif api_response:
        ret["API_Response"] = response

    errors = []
    # Iterate through API response and collect information
    for event in response:
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
            _push_status(ret, event)
        elif event_type == "errorDetail":
            _error_detail(errors, event)

    if errors:
        ret["Errors"] = errors
        ret["retcode"] = 1
    return ret