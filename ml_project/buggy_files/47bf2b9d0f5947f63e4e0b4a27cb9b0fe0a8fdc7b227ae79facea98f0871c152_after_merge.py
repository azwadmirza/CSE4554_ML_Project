def _register_internal_trigger_type(trigger_definition):
    try:
        trigger_type_db = create_trigger_type_db(trigger_type=trigger_definition,
                                                 log_not_unique_error_as_debug=True)
    except (NotUniqueError, StackStormDBObjectConflictError):
        # We ignore conflict error since this operation is idempotent and race is not an issue
        LOG.debug('Internal trigger type "%s" already exists, ignoring error...' %
                  (trigger_definition['name']))

        ref = ResourceReference.to_string_reference(name=trigger_definition['name'],
                                                    pack=trigger_definition['pack'])
        trigger_type_db = get_trigger_type_db(ref)

    if trigger_type_db:
        LOG.debug('Registered internal trigger: %s.', trigger_definition['name'])

    # trigger types with parameters do no require a shadow trigger.
    if trigger_type_db and not trigger_type_db.parameters_schema:
        try:
            trigger_db = create_shadow_trigger(trigger_type_db,
                log_not_unique_error_as_debug=True)

            extra = {'trigger_db': trigger_db}
            LOG.audit('Trigger created for parameter-less internal TriggerType. Trigger.id=%s' %
                      (trigger_db.id), extra=extra)
        except (NotUniqueError, StackStormDBObjectConflictError):
            LOG.debug('Shadow trigger "%s" already exists. Ignoring.',
                      trigger_type_db.get_reference().ref, exc_info=True)

        except (ValidationError, ValueError):
            LOG.exception('Validation failed in shadow trigger. TriggerType=%s.',
                          trigger_type_db.get_reference().ref)
            raise

    return trigger_type_db