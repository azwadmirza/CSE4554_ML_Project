def _get_extension_instance_name(instance_view, publisher, extension_type_name,
                                 suggested_name=None):
    extension_instance_name = suggested_name or extension_type_name
    full_type_name = '.'.join([publisher, extension_type_name])
    if instance_view.extensions:
        ext = next((x for x in instance_view.extensions
                    if x.type.lower() == full_type_name.lower()), None)
        if ext:
            extension_instance_name = ext.name
    return extension_instance_name