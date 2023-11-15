    def copy_model_obj(old_parent, new_parent, model, obj, creater, copy_name='', create_kwargs=None):
        fields_to_preserve = set(getattr(model, 'FIELDS_TO_PRESERVE_AT_COPY', []))
        fields_to_discard = set(getattr(model, 'FIELDS_TO_DISCARD_AT_COPY', []))
        m2m_to_preserve = {}
        o2m_to_preserve = {}
        create_kwargs = create_kwargs or {}
        for field_name in fields_to_discard:
            create_kwargs.pop(field_name, None)
        for field in model._meta.get_fields():
            try:
                field_val = getattr(obj, field.name)
            except AttributeError:
                continue
            # Adjust copy blacklist fields here.
            if field.name in fields_to_discard or field.name in [
                'id', 'pk', 'polymorphic_ctype', 'unifiedjobtemplate_ptr', 'created_by', 'modified_by'
            ] or field.name.endswith('_role'):
                create_kwargs.pop(field.name, None)
                continue
            if field.one_to_many:
                if field.name in fields_to_preserve:
                    o2m_to_preserve[field.name] = field_val
            elif field.many_to_many:
                if field.name in fields_to_preserve and not old_parent:
                    m2m_to_preserve[field.name] = field_val
            elif field.many_to_one and not field_val:
                create_kwargs.pop(field.name, None)
            elif field.many_to_one and field_val == old_parent:
                create_kwargs[field.name] = new_parent
            elif field.name == 'name' and not old_parent:
                create_kwargs[field.name] = copy_name or field_val + ' copy'
            elif field.name in fields_to_preserve:
                create_kwargs[field.name] = CopyAPIView._decrypt_model_field_if_needed(
                    obj, field.name, field_val
                )
        new_obj = model.objects.create(**create_kwargs)
        # Need to save separatedly because Djang-crum get_current_user would
        # not work properly in non-request-response-cycle context.
        new_obj.created_by = creater
        new_obj.save()
        for m2m in m2m_to_preserve:
            for related_obj in m2m_to_preserve[m2m].all():
                getattr(new_obj, m2m).add(related_obj)
        if not old_parent:
            sub_objects = []
            for o2m in o2m_to_preserve:
                for sub_obj in o2m_to_preserve[o2m].all():
                    sub_model = type(sub_obj)
                    sub_objects.append((sub_model.__module__, sub_model.__name__, sub_obj.pk))
            return new_obj, sub_objects
        ret = {obj: new_obj}
        for o2m in o2m_to_preserve:
            for sub_obj in o2m_to_preserve[o2m].all():
                ret.update(CopyAPIView.copy_model_obj(obj, new_obj, type(sub_obj), sub_obj, creater))
        return ret