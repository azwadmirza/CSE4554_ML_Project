def update_squash_addon(apps, schema_editor):
    """Update events setup for weblate.git.squash addon."""
    Addon = apps.get_model("addons", "Addon")
    Event = apps.get_model("addons", "Event")
    db_alias = schema_editor.connection.alias
    for addon in Addon.objects.using(db_alias).filter(name="weblate.git.squash"):
        Event.objects.using(db_alias).get_or_create(
            addon=addon, event=EVENT_POST_COMMIT
        )
        addon.event_set.filter(event=EVENT_PRE_PUSH).delete()