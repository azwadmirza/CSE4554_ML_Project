def create_shadow_trigger(trigger_type_db, log_not_unique_error_as_debug=False):
    """
    Create a shadow trigger for TriggerType with no parameters.

    :param log_not_unique_error_as_debug: True to lot NotUnique errors under debug instead of
                                          error log level. This is to be used in scenarios where
                                          failure is non-fatal (e.g. when services register
                                          internal trigger types which is an idempotent
                                          operation).
    :type log_not_unique_error_as_debug: ``bool``

    """
    trigger_type_ref = trigger_type_db.get_reference().ref

    if trigger_type_db.parameters_schema:
        LOG.debug('Skip shadow trigger for TriggerType with parameters %s.', trigger_type_ref)
        return None

    trigger = {'name': trigger_type_db.name,
               'pack': trigger_type_db.pack,
               'type': trigger_type_ref,
               'parameters': {}}

    return create_or_update_trigger_db(trigger,
                                       log_not_unique_error_as_debug=log_not_unique_error_as_debug)