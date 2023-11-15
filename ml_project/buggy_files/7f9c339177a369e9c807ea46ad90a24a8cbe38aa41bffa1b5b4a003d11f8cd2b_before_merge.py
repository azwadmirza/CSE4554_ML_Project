def remove_unusednewbase_alert(apps, schema_editor):
    Alert = apps.get_model("trans", "Alert")
    Alert.objects.filter(name="UnusedNewBase").delete()