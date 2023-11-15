def migrate_dashboard(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    db_alias = schema_editor.connection.alias
    Profile.objects.using(db_alias).filter(dashboard_view=2).update(dashboard_view=1)