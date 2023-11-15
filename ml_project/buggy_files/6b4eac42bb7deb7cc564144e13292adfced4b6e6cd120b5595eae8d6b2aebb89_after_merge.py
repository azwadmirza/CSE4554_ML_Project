def setup_listeners(config):
    # Register basic subscriber predicates, to filter events.
    config.add_subscriber_predicate('for_actions', EventActionFilter)
    config.add_subscriber_predicate('for_resources', EventResourceFilter)

    write_actions = (ACTIONS.CREATE, ACTIONS.UPDATE, ACTIONS.DELETE)
    settings = config.get_settings()
    project_name = settings.get('project_name', '')
    listeners = aslist(settings['event_listeners'])

    for name in listeners:
        logger.info('Setting up %r listener' % name)
        prefix = 'event_listeners.%s.' % name

        try:
            listener_mod = config.maybe_dotted(name)
            prefix = 'event_listeners.%s.' % name.split('.')[-1]
            listener = listener_mod.load_from_config(config, prefix)
        except (ImportError, AttributeError):
            module_setting = prefix + "use"
            # Read from ENV or settings.
            module_value = utils.read_env(project_name + "." + module_setting,
                                          settings.get(module_setting))
            listener_mod = config.maybe_dotted(module_value)
            listener = listener_mod.load_from_config(config, prefix)

        # If StatsD is enabled, monitor execution time of listeners.
        if getattr(config.registry, "statsd", None):
            statsd_client = config.registry.statsd
            key = 'listeners.%s' % name
            listener = statsd_client.timer(key)(listener.__call__)

        # Optional filter by event action.
        actions_setting = prefix + "actions"
        # Read from ENV or settings.
        actions_value = utils.read_env(project_name + "." + actions_setting,
                                       settings.get(actions_setting, ""))
        actions = aslist(actions_value)
        if len(actions) > 0:
            actions = ACTIONS.from_string_list(actions)
        else:
            actions = write_actions

        # Optional filter by event resource name.
        resource_setting = prefix + "resources"
        # Read from ENV or settings.
        resource_value = utils.read_env(project_name + "." + resource_setting,
                                        settings.get(resource_setting, ""))
        resource_names = aslist(resource_value)

        # Pyramid event predicates.
        options = dict(for_actions=actions, for_resources=resource_names)

        if ACTIONS.READ in actions:
            config.add_subscriber(listener, ResourceRead, **options)
            if len(actions) == 1:
                return

        config.add_subscriber(listener, ResourceChanged, **options)