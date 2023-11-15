def _lock_store_is_redis_lock_store(
    lock_store: Union[EndpointConfig, LockStore, None]
) -> bool:
    # determine whether `lock_store` is associated with a `RedisLockStore`
    if isinstance(lock_store, LockStore):
        if isinstance(lock_store, RedisLockStore):
            return True
        return False

    # `lock_store` is `None` or `EndpointConfig`
    return lock_store is not None and lock_store.type == "redis"