def migrate_tm(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    apps.get_model("trans", "Project").objects.using(db_alias).all().update(
        contribute_shared_tm=F("use_shared_tm")
    )