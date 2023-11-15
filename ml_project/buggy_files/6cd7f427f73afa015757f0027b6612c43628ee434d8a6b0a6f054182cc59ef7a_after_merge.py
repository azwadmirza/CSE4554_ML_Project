def patch_channels_asgi_handler_impl(cls):
    # type: (Any) -> None

    import channels  # type: ignore
    from sentry_sdk.integrations.django import DjangoIntegration

    if channels.__version__ < "3.0.0":

        old_app = cls.__call__

        async def sentry_patched_asgi_handler(self, receive, send):
            # type: (Any, Any, Any) -> Any
            if Hub.current.get_integration(DjangoIntegration) is None:
                return await old_app(self, receive, send)

            middleware = SentryAsgiMiddleware(
                lambda _scope: old_app.__get__(self, cls), unsafe_context_data=True
            )

            return await middleware(self.scope)(receive, send)

        cls.__call__ = sentry_patched_asgi_handler

    else:
        # The ASGI handler in Channels >= 3 has the same signature as
        # the Django handler.
        patch_django_asgi_handler_impl(cls)