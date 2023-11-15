def update_linked(apps, schema_editor):
    """Clean branch for linked components."""
    Component = apps.get_model("trans", "Component")
    db_alias = schema_editor.connection.alias
    linked = Component.objects.using(db_alias).filter(repo__startswith="weblate:")
    linked.update(branch="")