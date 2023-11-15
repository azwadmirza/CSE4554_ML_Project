def try_it(
    f: Callable[..., Any],
    ex: Any,
    ex_code: Optional[str] = None,
    base: float = 1.0,
    max_num_tries: int = 3,
    **kwargs: Any,
) -> Any:
    """Run function with decorrelated Jitter.

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    delay: float = base
    for i in range(max_num_tries):
        try:
            return f(**kwargs)
        except ex as exception:
            if ex_code is not None and hasattr(exception, "response"):
                if exception.response["Error"]["Code"] != ex_code:
                    raise
            if i == (max_num_tries - 1):
                raise
            delay = random.uniform(base, delay * 3)
            _logger.error("Retrying %s | Fail number %s/%s | Exception: %s", f, i + 1, max_num_tries, exception)
            time.sleep(delay)