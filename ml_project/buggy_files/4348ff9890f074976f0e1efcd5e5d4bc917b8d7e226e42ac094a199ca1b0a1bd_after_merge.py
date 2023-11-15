def includeme(config):
    settings = config.get_settings()

    # Heartbeat registry.
    config.registry.heartbeats = {}

    # Public settings registry.
    config.registry.public_settings = {'batch_max_requests', 'readonly'}

    # Directive to declare arbitrary API capabilities.
    def add_api_capability(config, identifier, description="", url="", **kw):
        existing = config.registry.api_capabilities.get(identifier)
        if existing:
            error_msg = "The '%s' API capability was already registered (%s)."
            raise ValueError(error_msg % (identifier, existing))

        capability = dict(description=description, url=url, **kw)
        config.registry.api_capabilities[identifier] = capability

    config.add_directive('add_api_capability', add_api_capability)
    config.registry.api_capabilities = {}

    # Setup cornice.
    config.include("cornice")

    # Per-request transaction.
    config.include("pyramid_tm")

    # Add CORS settings to the base cliquet Service class.
    Service.init_from_settings(settings)

    # Setup components.
    for step in aslist(settings['initialization_sequence']):
        step_func = config.maybe_dotted(step)
        step_func(config)

    # Custom helpers.
    config.add_request_method(follow_subrequest)
    config.add_request_method(lambda request: {'id': request.prefixed_userid},
                              name='get_user_info')
    config.commit()

    # Include cliquet plugins after init, unlike pyramid includes.
    includes = aslist(settings['includes'])
    for app in includes:
        config.include(app)

    # # Show settings to output.
    # for key, value in settings.items():
    #     logger.info('Using %s = %s' % (key, value))

    # Scan views.
    config.scan("cliquet.views")

    # Give sign of life.
    msg = "%(project_name)s %(project_version)s starting."
    logger.info(msg % settings)