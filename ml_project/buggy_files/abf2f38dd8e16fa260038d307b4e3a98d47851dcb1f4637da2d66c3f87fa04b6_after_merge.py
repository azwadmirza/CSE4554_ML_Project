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

        # TODO: remove this when we drop Python 2 support (functools.wraps
        # adds __wrapped__ automatically in later versions)
        public_api.__wrapped__ = implementation

        return public_api