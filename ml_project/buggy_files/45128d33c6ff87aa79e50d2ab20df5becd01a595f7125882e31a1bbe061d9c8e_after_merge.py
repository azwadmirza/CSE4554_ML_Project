def create_or_update_trigger_type_db(trigger_type, log_not_unique_error_as_debug=False):
    """
    Create or update a trigger type db object in the db given trigger_type definition as dict.

    :param trigger_type: Trigger type model.
    :type trigger_type: ``dict``

    :param log_not_unique_error_as_debug: True to lot NotUnique errors under debug instead of
                                          error log level. This is to be used in scenarios where
                                          failure is non-fatal (e.g. when services register
                                          internal trigger types which is an idempotent
                                          operation).
    :type log_not_unique_error_as_debug: ``bool``

    :rtype: ``object``
    """
    assert isinstance(trigger_type, dict)

    trigger_type_api = TriggerTypeAPI(**trigger_type)
    trigger_type_api.validate()
    trigger_type_api = TriggerTypeAPI.to_model(trigger_type_api)

    ref = ResourceReference.to_string_reference(name=trigger_type_api.name,
                                                pack=trigger_type_api.pack)

    existing_trigger_type_db = get_trigger_type_db(ref)
    if existing_trigger_type_db:
        is_update = True
    else:
        is_update = False

    if is_update:
        trigger_type_api.id = existing_trigger_type_db.id

    try:
        trigger_type_db = TriggerType.add_or_update(trigger_type_api,
            log_not_unique_error_as_debug=log_not_unique_error_as_debug)
    except StackStormDBObjectConflictError:
        # Operation is idempotent and trigger could have already been created by
        # another process. Ignore object already exists because it simply means
        # there was a race and object is already in the database.
        trigger_type_db = get_trigger_type_db(ref)
        is_update = True

    extra = {'trigger_type_db': trigger_type_db}

    if is_update:
        LOG.audit('TriggerType updated. TriggerType.id=%s' % (trigger_type_db.id), extra=extra)
    else:
        LOG.audit('TriggerType created. TriggerType.id=%s' % (trigger_type_db.id), extra=extra)

    return trigger_type_db