def remove_unusednewbase_alert(apps, schema_editor):
    Alert = apps.get_model("trans", "Alert")
    db_alias = schema_editor.connection.alias
    Alert.objects.using(db_alias).filter(name="UnusedNewBase").delete()