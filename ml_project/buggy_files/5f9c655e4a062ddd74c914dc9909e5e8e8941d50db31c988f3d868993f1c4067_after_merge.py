def setup_security(allowed_serializers=None, key=None, cert=None, store=None,
                   digest=None, serializer='json', app=None):
    """See :meth:`@Celery.setup_security`."""
    if app is None:
        from celery import current_app
        app = current_app._get_current_object()

    _disable_insecure_serializers(allowed_serializers)

    # check conf for sane security settings
    conf = app.conf
    if conf.task_serializer != 'auth' or conf.accept_content != ['auth']:
        raise ImproperlyConfigured(SETTING_MISSING)

    key = key or conf.security_key
    cert = cert or conf.security_certificate
    store = store or conf.security_cert_store
    digest = digest or conf.security_digest

    if not (key and cert and store):
        raise ImproperlyConfigured(SECURITY_SETTING_MISSING)

    with open(key, 'r') as kf:
        with open(cert, 'r') as cf:
            register_auth(kf.read(), cf.read(), store, digest, serializer)
    registry._set_default_serializer('auth')