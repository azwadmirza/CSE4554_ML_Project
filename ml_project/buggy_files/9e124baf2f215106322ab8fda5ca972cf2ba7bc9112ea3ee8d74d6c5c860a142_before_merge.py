def fix_repo_scope(apps, schema_editor):
    Addon = apps.get_model("addons", "Addon")
    Addon.objects.filter(name="weblate.git.squash").update(repo_scope=True)