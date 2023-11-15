def set_export_url(apps, schema_editor):
    SubProject = apps.get_model('trans', 'SubProject')
    matching = SubProject.objects.filter(
        vcs__in=SUPPORTED_VCS
    ).exclude(
        repo__startswith='weblate:/'
    )
    for component in matching:
        new_url = get_export_url(component)
        if component.git_export != new_url:
            component.git_export = new_url
            component.save()