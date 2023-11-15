def migrate_priority(apps, schema_editor):
    Source = apps.get_model("trans", "Source")
    db_alias = schema_editor.connection.alias
    for source in Source.objects.using(db_alias).exclude(priority=100).iterator():
        if source.check_flags:
            source.check_flags += ", "
        source.check_flags += "priority:{}".format(200 - source.priority)
        source.save(update_fields=["check_flags"])