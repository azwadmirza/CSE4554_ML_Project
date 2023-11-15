def update_repo_scope(apps, schema_editor):
    """Update the repo_scope flag."""
    Addon = apps.get_model("addons", "Addon")
    Addon.objects.filter(name="weblate.git.squash").update(repo_scope=True)