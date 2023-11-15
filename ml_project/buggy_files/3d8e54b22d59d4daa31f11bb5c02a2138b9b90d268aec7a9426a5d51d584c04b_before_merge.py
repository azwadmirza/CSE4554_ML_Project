    def setup_security(self, allowed_serializers=None, key=None, cert=None,
                       store=None, digest='sha1', serializer='json'):
        """Setup the message-signing serializer.

        This will affect all application instances (a global operation).

        Disables untrusted serializers and if configured to use the ``auth``
        serializer will register the ``auth`` serializer with the provided
        settings into the Kombu serializer registry.

        Arguments:
            allowed_serializers (Set[str]): List of serializer names, or
                content_types that should be exempt from being disabled.
            key (str): Name of private key file to use.
                Defaults to the :setting:`security_key` setting.
            cert (str): Name of certificate file to use.
                Defaults to the :setting:`security_certificate` setting.
            store (str): Directory containing certificates.
                Defaults to the :setting:`security_cert_store` setting.
            digest (str): Digest algorithm used when signing messages.
                Default is ``sha1``.
            serializer (str): Serializer used to encode messages after
                they've been signed.  See :setting:`task_serializer` for
                the serializers supported.  Default is ``json``.
        """
        from celery.security import setup_security
        return setup_security(allowed_serializers, key, cert,
                              store, digest, serializer, app=self)