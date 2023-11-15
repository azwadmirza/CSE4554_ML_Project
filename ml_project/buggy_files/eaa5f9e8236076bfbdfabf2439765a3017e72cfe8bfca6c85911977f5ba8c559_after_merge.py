def update_addon(apps, schema_editor):
    """Update the repo_scope flag."""
    Addon = apps.get_model("addons", "Addon")
    Event = apps.get_model("addons", "Event")
    db_alias = schema_editor.connection.alias
    for addon in Addon.objects.using(db_alias).filter(
        name="weblate.consistency.languages"
    ):
        Event.objects.using(db_alias).get_or_create(addon=addon, event=EVENT_DAILY)
        addon.event_set.filter(event=EVENT_POST_UPDATE).delete()