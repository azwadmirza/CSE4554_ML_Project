def register_internal_trigger_types():
    """
    Register internal trigger types.

    NOTE 1: This method blocks until all the trigger types have been registered.

    NOTE 2: We log "NotUniqueError" errors under debug and not error. Those errors are not fatal
    because this operation is idempotent and NotUniqueError simply means internal trigger type
    has already been registered by some other service.
    """
    action_sensor_enabled = cfg.CONF.action_sensor.enable

    registered_trigger_types_db = []

    for _, trigger_definitions in six.iteritems(INTERNAL_TRIGGER_TYPES):
        for trigger_definition in trigger_definitions:
            LOG.debug('Registering internal trigger: %s', trigger_definition['name'])

            is_action_trigger = trigger_definition['name'] == ACTION_SENSOR_TRIGGER['name']
            if is_action_trigger and not action_sensor_enabled:
                continue
            try:
                trigger_type_db = _register_internal_trigger_type(
                    trigger_definition=trigger_definition)
            except Exception:
                LOG.exception('Failed registering internal trigger: %s.', trigger_definition)
                raise
            else:
                registered_trigger_types_db.append(trigger_type_db)

    return registered_trigger_types_db