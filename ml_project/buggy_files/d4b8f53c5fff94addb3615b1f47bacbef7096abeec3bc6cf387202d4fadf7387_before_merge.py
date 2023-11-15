def unfix_alert_occurence(apps, schema_editor):
    Alert = apps.get_model("trans", "Alert")
    Alert.objects.filter(details__contains='"occurrences"').update(
        details=Func(
            F("details"),
            Value('"occurrences"'),
            Value('"occurences"'),
            function="replace",
        )
    )