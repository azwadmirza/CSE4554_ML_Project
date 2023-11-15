def memory(address, redis_password):
    """Print object references held in a Ray cluster."""
    if not address:
        address = services.find_redis_address_or_die()
    logger.info(f"Connecting to Ray instance at {address}.")
    ray.init(address=address, _redis_password=redis_password)
    print(ray.internal.internal_api.memory_summary())