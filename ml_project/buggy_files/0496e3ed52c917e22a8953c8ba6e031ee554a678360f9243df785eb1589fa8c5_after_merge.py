def resolve_auto_format(apps, schema_editor):
    Component = apps.get_model("trans", "Component")
    db_alias = schema_editor.connection.alias
    for component in Component.objects.using(db_alias).filter(file_format="auto"):
        path = get_path(component)
        template = None
        if component.template:
            template = AutodetectFormat.parse(os.path.join(path, component.template))
        try:
            translation = component.translation_set.all()[0]
        except IndexError:
            if template is None and component.new_base:
                template = AutodetectFormat.parse(
                    os.path.join(path, component.new_base)
                )
            if template is not None:
                update_format(component, template)
                continue
            raise Exception(
                "Existing translation component with auto format and "
                "without any translations, can not detect file format. "
                "Please edit the format manually and rerun migration. "
                "Affected component: {}/{}".format(
                    component.project.slug, component.slug
                )
            )
        store = AutodetectFormat.parse(
            os.path.join(path, translation.filename), template
        )
        update_format(component, store)