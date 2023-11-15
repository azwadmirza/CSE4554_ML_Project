def fix_alert_occurence(apps, schema_editor):
    Alert = apps.get_model("trans", "Alert")
    Alert.objects.filter(details__contains='"occurences"').update(
        details=Func(
            F("details"),
            Value('"occurences"'),
            Value('"occurrences"'),
            function="replace",
        )
    )