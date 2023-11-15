def create_trigger_type_db(trigger_type, log_not_unique_error_as_debug=False):
    """
    Creates a trigger type db object in the db given trigger_type definition as dict.

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
    trigger_type_api = TriggerTypeAPI(**trigger_type)
    trigger_type_api.validate()
    ref = ResourceReference.to_string_reference(name=trigger_type_api.name,
                                                pack=trigger_type_api.pack)
    trigger_type_db = get_trigger_type_db(ref)

    if not trigger_type_db:
        trigger_type_db = TriggerTypeAPI.to_model(trigger_type_api)
        LOG.debug('verified trigger and formulated TriggerDB=%s', trigger_type_db)
        trigger_type_db = TriggerType.add_or_update(trigger_type_db,
            log_not_unique_error_as_debug=log_not_unique_error_as_debug)

    return trigger_type_db