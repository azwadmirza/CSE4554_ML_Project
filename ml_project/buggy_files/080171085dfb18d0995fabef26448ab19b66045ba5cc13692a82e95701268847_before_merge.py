def create_shadow_trigger(trigger_type_db):
    """
    Create a shadow trigger for TriggerType with no parameters.
    """
    trigger_type_ref = trigger_type_db.get_reference().ref

    if trigger_type_db.parameters_schema:
        LOG.debug('Skip shadow trigger for TriggerType with parameters %s.', trigger_type_ref)
        return None

    trigger = {'name': trigger_type_db.name,
               'pack': trigger_type_db.pack,
               'type': trigger_type_ref,
               'parameters': {}}

    return create_or_update_trigger_db(trigger)