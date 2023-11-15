def set_export_url(apps, schema_editor):
    Component = apps.get_model("trans", "Component")
    db_alias = schema_editor.connection.alias
    matching = (
        Component.objects.using(db_alias)
        .filter(vcs__in=SUPPORTED_VCS)
        .exclude(repo__startswith="weblate:/")
    )
    for component in matching:
        new_url = get_export_url(component)
        if component.git_export != new_url:
            component.git_export = new_url
            component.save()