def fix_repo_scope(apps, schema_editor):
    Addon = apps.get_model("addons", "Addon")
    db_alias = schema_editor.connection.alias
    Addon.objects.using(db_alias).filter(name="weblate.git.squash").update(
        repo_scope=True
    )