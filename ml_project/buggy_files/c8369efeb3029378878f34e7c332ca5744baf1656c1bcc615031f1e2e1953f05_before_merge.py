def migrate_alert_change(apps, schema_editor):
    Change = apps.get_model("trans", "Change")
    for change in Change.objects.filter(action=47).exclude(target=""):
        change.details = {"alert": change.target}
        change.target = ""
        change.save()