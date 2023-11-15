def migrate_unitdata(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Unit = apps.get_model("trans", "Unit")

    for model_args, fields in MODELS:
        model = apps.get_model(*model_args)
        # Create new objects for each related unit
        for obj in model.objects.using(db_alias).filter(unit=None).iterator():
            units = Unit.objects.using(db_alias).filter(
                content_hash=obj.content_hash,
                translation__component__project=obj.project,
            )
            if obj.language is None:
                units = units.filter(translation__language=obj.project.source_language)
            else:
                units = units.filter(translation__language=obj.language)
            # Using __getstate__ would be cleaner, but needs Django 2.0
            state = {field: getattr(obj, field) for field in fields}
            for unit in units:
                if model.objects.using(db_alias).filter(unit=unit, **state).exists():
                    continue
                created = model.objects.using(db_alias).create(unit=unit, **state)
                # Migrate suggestion votes
                if model_args == ("trans", "Suggestion"):
                    for vote in obj.vote_set.all():
                        created.vote_set.create(user=vote.user, value=vote.value)

        # Remove old objects without unit link
        model.objects.using(db_alias).filter(unit=None).delete()