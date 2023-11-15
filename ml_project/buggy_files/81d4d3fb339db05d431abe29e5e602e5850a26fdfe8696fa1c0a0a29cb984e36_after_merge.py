def _create_from_endpoint_config(
    endpoint_config: Optional[EndpointConfig] = None,
) -> "LockStore":
    """Given an endpoint configuration, create a proper `LockStore` object."""

    if (
        endpoint_config is None
        or endpoint_config.type is None
        or endpoint_config.type == "in_memory"
    ):
        # this is the default type if no lock store type is set

        lock_store = InMemoryLockStore()
    elif endpoint_config.type == "redis":
        lock_store = RedisLockStore(host=endpoint_config.url, **endpoint_config.kwargs)
    else:
        lock_store = _load_from_module_string(endpoint_config)

    logger.debug(f"Connected to lock store '{lock_store.__class__.__name__}'.")

    return lock_store