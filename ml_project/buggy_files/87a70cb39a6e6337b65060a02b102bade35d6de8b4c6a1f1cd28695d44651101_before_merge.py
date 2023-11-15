def migrate_customfieldvalues(apps, schema_editor):
    """
    Copy data from CustomFieldValues into the custom_field_data JSON field on each model instance.
    """
    CustomFieldValue = apps.get_model('extras', 'CustomFieldValue')

    for cfv in CustomFieldValue.objects.prefetch_related('field').exclude(serialized_value=''):
        model = apps.get_model(cfv.obj_type.app_label, cfv.obj_type.model)

        # Read and update custom field value for each instance
        # TODO: This can be done more efficiently once .update() is supported for JSON fields
        cf_data = model.objects.filter(pk=cfv.obj_id).values('custom_field_data').first()
        try:
            cf_data['custom_field_data'][cfv.field.name] = deserialize_value(cfv.field, cfv.serialized_value)
        except ValueError as e:
            print(f'{cfv.field.name} ({cfv.field.type}): {cfv.serialized_value} ({cfv.pk})')
            raise e
        model.objects.filter(pk=cfv.obj_id).update(**cf_data)