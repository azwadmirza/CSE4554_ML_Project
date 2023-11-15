def setup_listeners(config):
    # Register basic subscriber predicates, to filter events.
    config.add_subscriber_predicate('for_actions', EventActionFilter)
    config.add_subscriber_predicate('for_resources', EventResourceFilter)

    write_actions = (ACTIONS.CREATE, ACTIONS.UPDATE, ACTIONS.DELETE)
    settings = config.get_settings()
    listeners = aslist(settings['event_listeners'])

    for name in listeners:
        logger.info('Setting up %r listener' % name)
        prefix = 'event_listeners.%s.' % name

        try:
            listener_mod = config.maybe_dotted(name)
            prefix = 'event_listeners.%s.' % name.split('.')[-1]
            listener = listener_mod.load_from_config(config, prefix)
        except (ImportError, AttributeError):
            listener_mod = config.maybe_dotted(settings[prefix + 'use'])
            listener = listener_mod.load_from_config(config, prefix)

        # If StatsD is enabled, monitor execution time of listeners.
        if getattr(config.registry, "statsd", None):
            statsd_client = config.registry.statsd
            key = 'listeners.%s' % name
            listener = statsd_client.timer(key)(listener.__call__)

        actions = aslist(settings.get(prefix + 'actions', ''))
        if len(actions) > 0:
            actions = ACTIONS.from_string_list(actions)
        else:
            actions = write_actions

        resource_names = aslist(settings.get(prefix + 'resources', ''))
        options = dict(for_actions=actions, for_resources=resource_names)

        if ACTIONS.READ in actions:
            config.add_subscriber(listener, ResourceRead, **options)
            if len(actions) == 1:
                return

        config.add_subscriber(listener, ResourceChanged, **options)