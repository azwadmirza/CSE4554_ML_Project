def migrate_editor(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    db_alias = schema_editor.connection.alias
    for profile in Profile.objects.using(db_alias).exclude(editor_link=""):
        profile.editor_link = weblate.utils.render.migrate_repoweb(profile.editor_link)
        profile.save()