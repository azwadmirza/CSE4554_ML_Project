def migrate_votes(apps, schema_editor):
    if not table_has_row(schema_editor.connection, "trans_vote", "positive"):
        return
    Vote = apps.get_model("trans", "Vote")
    Vote.objects.filter(positive=True).update(value=1)
    Vote.objects.filter(positive=False).update(value=-1)