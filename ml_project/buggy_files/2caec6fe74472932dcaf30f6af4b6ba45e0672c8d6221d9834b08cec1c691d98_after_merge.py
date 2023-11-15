def backwards(apps, schema_editor):
    change_foreign_keys(apps, schema_editor,
                        "weblate_auth", "User",
                        "auth", "User")