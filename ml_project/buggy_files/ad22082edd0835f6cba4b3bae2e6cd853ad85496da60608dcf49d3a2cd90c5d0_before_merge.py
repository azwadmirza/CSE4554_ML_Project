def array_function_dispatch(dispatcher, module=None, verify=True):
    """Decorator for adding dispatch with the __array_function__ protocol."""
    def decorator(implementation):
        # TODO: only do this check when the appropriate flag is enabled or for
        # a dev install. We want this check for testing but don't want to
        # slow down all numpy imports.
        if verify:
            verify_matching_signatures(implementation, dispatcher)

        @functools.wraps(implementation)
        def public_api(*args, **kwargs):
            relevant_args = dispatcher(*args, **kwargs)
            return array_function_implementation_or_override(
                implementation, public_api, relevant_args, args, kwargs)

        if module is not None:
            public_api.__module__ = module

        return public_api

    return decorator