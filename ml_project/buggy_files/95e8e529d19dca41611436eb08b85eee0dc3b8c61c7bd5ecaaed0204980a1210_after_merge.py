def migrate_votes(apps, schema_editor):
    if not table_has_row(schema_editor.connection, "trans_vote", "positive"):
        return
    Vote = apps.get_model("trans", "Vote")
    db_alias = schema_editor.connection.alias
    Vote.objects.using(db_alias).filter(positive=True).update(value=1)
    Vote.objects.using(db_alias).filter(positive=False).update(value=-1)