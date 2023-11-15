def update_linked(apps, schema_editor):
    """Clean branch for linked components."""
    Component = apps.get_model("trans", "Component")
    linked = Component.objects.filter(repo__startswith="weblate:")
    linked.update(branch="")