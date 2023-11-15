def migrate_repoweb(apps, schema_editor):
    Component = apps.get_model("trans", "Component")
    for component in Component.objects.exclude(repoweb=""):
        component.repoweb = weblate.utils.render.migrate_repoweb(component.repoweb)
        component.save()