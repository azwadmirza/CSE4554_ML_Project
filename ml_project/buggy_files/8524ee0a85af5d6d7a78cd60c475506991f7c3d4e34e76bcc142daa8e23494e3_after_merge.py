def create_or_update_trigger_db(trigger, log_not_unique_error_as_debug=False):
    """
    Create a new TriggerDB model if one doesn't exist yet or update existing
    one.

    :param trigger: Trigger info.
    :type trigger: ``dict``
    """
    assert isinstance(trigger, dict)

    existing_trigger_db = _get_trigger_db(trigger)

    if existing_trigger_db:
        is_update = True
    else:
        is_update = False

    trigger_api = TriggerAPI(**trigger)
    trigger_api.validate()
    trigger_db = TriggerAPI.to_model(trigger_api)

    if is_update:
        trigger_db.id = existing_trigger_db.id

    trigger_db = Trigger.add_or_update(trigger_db,
        log_not_unique_error_as_debug=log_not_unique_error_as_debug)

    extra = {'trigger_db': trigger_db}

    if is_update:
        LOG.audit('Trigger updated. Trigger.id=%s' % (trigger_db.id), extra=extra)
    else:
        LOG.audit('Trigger created. Trigger.id=%s' % (trigger_db.id), extra=extra)

    return trigger_db