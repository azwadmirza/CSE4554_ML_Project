def migrate_editor(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    for profile in Profile.objects.exclude(editor_link=""):
        profile.editor_link = weblate.utils.render.migrate_repoweb(profile.editor_link)
        profile.save()