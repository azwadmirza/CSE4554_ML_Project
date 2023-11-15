def migrate_alert_change(apps, schema_editor):
    Change = apps.get_model("trans", "Change")
    db_alias = schema_editor.connection.alias
    for change in Change.objects.using(db_alias).filter(action=47).exclude(target=""):
        change.details = {"alert": change.target}
        change.target = ""
        change.save()