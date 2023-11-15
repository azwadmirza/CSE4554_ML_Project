def setup_security(allowed_serializers=None, key=None, cert=None, store=None,
                   digest='sha1', serializer='json', app=None):
    """See :meth:`@Celery.setup_security`."""
    if app is None:
        from celery import current_app
        app = current_app._get_current_object()

    _disable_insecure_serializers(allowed_serializers)

    conf = app.conf
    if conf.task_serializer != 'auth':
        return

    try:
        from OpenSSL import crypto  # noqa
    except ImportError:
        raise ImproperlyConfigured(SSL_NOT_INSTALLED)

    key = key or conf.security_key
    cert = cert or conf.security_certificate
    store = store or conf.security_cert_store

    if not (key and cert and store):
        raise ImproperlyConfigured(SETTING_MISSING)

    with open(key) as kf:
        with open(cert) as cf:
            register_auth(kf.read(), cf.read(), store, digest, serializer)
    registry._set_default_serializer('auth')