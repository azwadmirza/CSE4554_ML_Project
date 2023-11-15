async def watch_objs(
        *,
        settings: configuration.OperatorSettings,
        resource: resources.Resource,
        namespace: Optional[str] = None,
        timeout: Optional[float] = None,
        since: Optional[str] = None,
        context: Optional[auth.APIContext] = None,  # injected by the decorator
        freeze_waiter: asyncio_Future,
) -> AsyncIterator[bodies.RawInput]:
    """
    Watch objects of a specific resource type.

    The cluster-scoped call is used in two cases:

    * The resource itself is cluster-scoped, and namespacing makes not sense.
    * The operator serves all namespaces for the namespaced custom resource.

    Otherwise, the namespace-scoped call is used:

    * The resource is namespace-scoped AND operator is namespaced-restricted.
    """
    if context is None:
        raise RuntimeError("API instance is not injected by the decorator.")

    is_namespaced = await discovery.is_namespaced(resource=resource, context=context)
    namespace = namespace if is_namespaced else None

    params: Dict[str, str] = {}
    params['watch'] = 'true'
    if since is not None:
        params['resourceVersion'] = since
    if timeout is not None:
        params['timeoutSeconds'] = str(timeout)

    # Talk to the API and initiate a streaming response.
    response = await context.session.get(
        url=resource.get_url(server=context.server, namespace=namespace, params=params),
        timeout=aiohttp.ClientTimeout(
            total=settings.watching.client_timeout,
            sock_connect=settings.watching.connect_timeout,
        ),
    )
    response.raise_for_status()

    # Stream the parsed events from the response until it is closed server-side,
    # or until it is closed client-side by the freeze-waiting future's callbacks.
    response_close_callback = lambda _: response.close()
    freeze_waiter.add_done_callback(response_close_callback)
    try:
        async with response:
            async for line in _iter_jsonlines(response.content):
                raw_input = cast(bodies.RawInput, json.loads(line.decode("utf-8")))
                yield raw_input
    except (aiohttp.ClientConnectionError, aiohttp.ClientPayloadError, asyncio.TimeoutError):
        pass
    finally:
        freeze_waiter.remove_done_callback(response_close_callback)