def migrate_subscriptions(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    db_alias = schema_editor.connection.alias
    profiles = Profile.objects.using(db_alias).all().select_related("user")
    profiles = profiles.exclude(user__username=settings.ANONYMOUS_USER_NAME)
    for profile in profiles:
        user = profile.user
        create_default_notifications(user)
        for flag, notifications in MAPPING:
            if getattr(profile, flag):
                for notification in notifications:
                    user.subscription_set.get_or_create(
                        scope=SCOPE_DEFAULT,
                        notification=notification,
                        defaults={"frequency": FREQ_INSTANT},
                    )