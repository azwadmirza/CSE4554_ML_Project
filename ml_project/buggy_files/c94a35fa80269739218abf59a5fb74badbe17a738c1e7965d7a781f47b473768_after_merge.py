def create_profiles(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    User = apps.get_model("weblate_auth", "User")
    db_alias = schema_editor.connection.alias
    for user in User.objects.using(db_alias).iterator():
        Profile.objects.using(db_alias).get_or_create(user=user)