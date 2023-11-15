def activity_stream_create(sender, instance, created, **kwargs):
    if created and activity_stream_enabled:
        _type = type(instance)
        if getattr(_type, '_deferred', False):
            return
        object1 = camelcase_to_underscore(instance.__class__.__name__)
        changes = model_to_dict(instance, model_serializer_mapping())
        # Special case where Job survey password variables need to be hidden
        if type(instance) == Job:
            changes['credentials'] = [
                '{} ({})'.format(c.name, c.id)
                for c in instance.credentials.iterator()
            ]
            changes['labels'] = [l.name for l in instance.labels.iterator()]
            if 'extra_vars' in changes:
                changes['extra_vars'] = instance.display_extra_vars()
        if type(instance) == OAuth2AccessToken:
            changes['token'] = CENSOR_VALUE
        activity_entry = get_activity_stream_class()(
            operation='create',
            object1=object1,
            changes=json.dumps(changes),
            actor=get_current_user_or_none())
        #TODO: Weird situation where cascade SETNULL doesn't work
        #      it might actually be a good idea to remove all of these FK references since
        #      we don't really use them anyway.
        if instance._meta.model_name != 'setting':  # Is not conf.Setting instance
            activity_entry.save()
            getattr(activity_entry, object1).add(instance.pk)
        else:
            activity_entry.setting = conf_to_dict(instance)
            activity_entry.save()
        connection.on_commit(
            lambda: emit_activity_stream_change(activity_entry)
        )