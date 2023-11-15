def update_resx_addon(apps, schema_editor):
    Addon = apps.get_model("addons", "Addon")
    Addon.objects.filter(
        component__file_format="resx", name="weblate.cleanup.generic"
    ).update(name="weblate.resx.update")