def update_squash_addon(apps, schema_editor):
    """Update events setup for weblate.git.squash addon."""
    Addon = apps.get_model("addons", "Addon")
    Event = apps.get_model("addons", "Event")
    for addon in Addon.objects.filter(name="weblate.git.squash"):
        Event.objects.get_or_create(addon=addon, event=EVENT_POST_COMMIT)
        addon.event_set.filter(event=EVENT_PRE_PUSH).delete()