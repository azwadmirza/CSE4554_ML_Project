def resolve_auto_format(apps, schema_editor):
    Addon = apps.get_model("addons", "Addon")
    for addon in Addon.objects.filter(name="weblate.discovery.discovery"):
        if addon.configuration["file_format"] == "auto":
            detect = detect_filename(addon.configuration["match"].replace("\\.", "."))
            if detect is None:
                raise Exception(
                    "Existing component discovery with auto format, can not detect "
                    "file format. Please edit the format manually and rerun "
                    "migration. Affected component: {}/{}".format(
                        addon.component.project.slug, addon.component.slug
                    )
                )

            addon.configuration["file_format"] = detect.format_id
            addon.save()