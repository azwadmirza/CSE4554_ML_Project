def migrate_dashboard(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    Profile.objects.filter(dashboard_view=2).update(dashboard_view=1)