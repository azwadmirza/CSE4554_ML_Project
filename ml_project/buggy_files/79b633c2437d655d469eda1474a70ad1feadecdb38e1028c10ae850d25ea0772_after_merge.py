def activity_stream_delete(sender, instance, **kwargs):
    if not activity_stream_enabled:
        return
    # Inventory delete happens in the task system rather than request-response-cycle.
    # If we trigger this handler there we may fall into db-integrity-related race conditions.
    # So we add flag verification to prevent normal signal handling. This funciton will be
    # explicitly called with flag on in Inventory.schedule_deletion.
    changes = {}
    if isinstance(instance, Inventory):
        if not kwargs.get('inventory_delete_flag', False):
            return
        # Add additional data about child hosts / groups that will be deleted
        changes['coalesced_data'] = {
            'hosts_deleted': instance.hosts.count(),
            'groups_deleted': instance.groups.count()
        }
    elif isinstance(instance, (Host, Group)) and instance.inventory.pending_deletion:
        return  # accounted for by inventory entry, above
    _type = type(instance)
    if getattr(_type, '_deferred', False):
        return
    changes.update(model_to_dict(instance, model_serializer_mapping()))
    object1 = camelcase_to_underscore(instance.__class__.__name__)
    if type(instance) == OAuth2AccessToken:
        changes['token'] = CENSOR_VALUE
    activity_entry = get_activity_stream_class()(
        operation='delete',
        changes=json.dumps(changes),
        object1=object1,
        actor=get_current_user_or_none())
    activity_entry.save()
    connection.on_commit(
        lambda: emit_activity_stream_change(activity_entry)
    )