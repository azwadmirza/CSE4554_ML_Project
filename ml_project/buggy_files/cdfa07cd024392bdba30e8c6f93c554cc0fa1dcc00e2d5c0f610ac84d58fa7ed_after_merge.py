def migrate_repoweb(apps, schema_editor):
    Component = apps.get_model("trans", "Component")
    db_alias = schema_editor.connection.alias
    for component in Component.objects.using(db_alias).exclude(repoweb=""):
        component.repoweb = weblate.utils.render.migrate_repoweb(component.repoweb)
        component.save()