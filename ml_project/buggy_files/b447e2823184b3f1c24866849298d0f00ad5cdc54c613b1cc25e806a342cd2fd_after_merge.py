def forwards(apps, schema_editor):
    change_foreign_keys(apps, schema_editor,
                        "auth", "User",
                        "weblate_auth", "User")