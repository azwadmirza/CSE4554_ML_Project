def migrate_flags(apps, schema_editor):
    """Update the repo_scope flag."""
    Addon = apps.get_model("addons", "Addon")
    db_alias = schema_editor.connection.alias
    Addon.objects.using(db_alias).filter(
        name__in=("weblate.discovery.discovery", "weblate.git.squash")
    ).update(repo_scope=True)
    Addon.objects.using(db_alias).filter(
        name__in=("weblate.removal.comments", "weblate.removal.suggestions")
    ).update(project_scope=True)