def setup_app(config={}):
    LOG.info('Creating st2api: %s as OpenAPI app.', VERSION_STRING)

    is_gunicorn = config.get('is_gunicorn', False)
    if is_gunicorn:
        # Note: We need to perform monkey patching in the worker. If we do it in
        # the master process (gunicorn_config.py), it breaks tons of things
        # including shutdown
        monkey_patch()

        st2api_config.register_opts()
        # This should be called in gunicorn case because we only want
        # workers to connect to db, rabbbitmq etc. In standalone HTTP
        # server case, this setup would have already occurred.
        common_setup(service='api', config=st2api_config, setup_db=True,
                     register_mq_exchanges=True,
                     register_signal_handlers=True,
                     register_internal_trigger_types=True,
                     run_migrations=True,
                     config_args=config.get('config_args', None))

    # Additional pre-run time checks
    validate_rbac_is_correctly_configured()

    router = Router(debug=cfg.CONF.api.debug, auth=cfg.CONF.auth.enable)

    spec = spec_loader.load_spec('st2common', 'openapi.yaml.j2')
    transforms = {
        '^/api/v1/': ['/', '/v1/', '/v1'],
        '^/api/v1/executions': ['/actionexecutions', '/v1/actionexecutions'],
        '^/api/exp/': ['/exp/']
    }
    router.add_spec(spec, transforms=transforms)

    app = router.as_wsgi

    # Order is important. Check middleware for detailed explanation.
    app = StreamingMiddleware(app, path_whitelist=['/v1/executions/*/output*'])
    app = ErrorHandlingMiddleware(app)
    app = CorsMiddleware(app)
    app = LoggingMiddleware(app, router)
    app = RequestIDMiddleware(app)

    return app