def fix_alert_occurence(apps, schema_editor):
    Alert = apps.get_model("trans", "Alert")
    db_alias = schema_editor.connection.alias
    Alert.objects.using(db_alias).filter(details__contains='"occurences"').update(
        details=Func(
            F("details"),
            Value('"occurences"'),
            Value('"occurrences"'),
            function="replace",
        )
    )