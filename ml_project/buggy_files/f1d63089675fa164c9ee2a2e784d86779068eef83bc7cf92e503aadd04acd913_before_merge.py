def migrate_tm(apps, schema_editor):
    apps.get_model("trans", "Project").objects.all().update(
        contribute_shared_tm=F("use_shared_tm")
    )