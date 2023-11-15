def create_profiles(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    User = apps.get_model("weblate_auth", "User")
    for user in User.objects.iterator():
        Profile.objects.get_or_create(user=user)