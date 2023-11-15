def _lock_store_is_redis_lock_store(
    lock_store: Union[EndpointConfig, LockStore, None]
) -> bool:
    if isinstance(lock_store, RedisLockStore):
        return True

    if isinstance(lock_store, LockStore):
        return False

    # `lock_store` is `None` or `EndpointConfig`
    return lock_store is not None and lock_store.type == "redis"