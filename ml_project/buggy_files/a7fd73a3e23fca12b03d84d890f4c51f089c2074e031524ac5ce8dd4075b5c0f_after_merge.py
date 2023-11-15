                def run(*args, **kwargs):
                    try:
                        return task._orig_run(*args, **kwargs)
                    except Ignore:
                        # If Ignore signal occures task shouldn't be retried,
                        # even if it suits autoretry_for list
                        raise
                    except Retry:
                        raise
                    except autoretry_for as exc:
                        if retry_backoff:
                            retry_kwargs['countdown'] = \
                                get_exponential_backoff_interval(
                                    factor=retry_backoff,
                                    retries=task.request.retries,
                                    maximum=retry_backoff_max,
                                    full_jitter=retry_jitter)
                        raise task.retry(exc=exc, **retry_kwargs)