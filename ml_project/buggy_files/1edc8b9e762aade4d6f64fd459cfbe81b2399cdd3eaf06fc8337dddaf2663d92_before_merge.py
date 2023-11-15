def is_limit_reached(num_messages: int, limit: int) -> bool:
    return limit is not None and num_messages >= limit