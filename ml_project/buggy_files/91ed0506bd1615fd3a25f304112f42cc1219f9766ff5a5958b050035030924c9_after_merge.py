def send_notification(issue, op, conf):
    notify_backend = conf.get('notifications', 'backend')

    if notify_backend == 'pynotify':
        warnings.warn("pynotify is deprecated.  Use backend=gobject.  "
                      "See https://github.com/ralphbean/bugwarrior/issues/336")
        notify_backend = 'gobject'

    # Notifications for growlnotify on Mac OS X
    if notify_backend == 'growlnotify':
        import gntp.notifier
        growl = gntp.notifier.GrowlNotifier(
            applicationName="Bugwarrior",
            notifications=["New Updates", "New Messages"],
            defaultNotifications=["New Messages"],
        )
        growl.register()
        if op == 'bw_finished':
            growl.notify(
                noteType="New Messages",
                title="Bugwarrior",
                description="Finished querying for new issues.\n%s" %
                issue['description'],
                sticky=asbool(conf.get(
                    'notifications', 'finished_querying_sticky', 'True')),
                icon="https://upload.wikimedia.org/wikipedia/"
                "en/5/59/Taskwarrior_logo.png",
                priority=1,
            )
            return
        message = "%s task: %s" % (op, issue['description'])
        metadata = _get_metadata(issue)
        if metadata is not None:
            message += metadata
        growl.notify(
            noteType="New Messages",
            title="Bugwarrior",
            description=message,
            sticky=asbool(conf.get(
                'notifications', 'task_crud_sticky', 'True')),
            icon="https://upload.wikimedia.org/wikipedia/"
            "en/5/59/Taskwarrior_logo.png",
            priority=1,
        )
        return
    elif notify_backend == 'gobject':
        _cache_logo()

        import gi
        gi.require_version('Notify', '0.7')
        from gi.repository import Notify
        Notify.init("bugwarrior")

        if op == 'bw finished':
            message = "Finished querying for new issues.\n%s" %\
                issue['description']
        else:
            message = "%s task: %s" % (op, issue['description'])
            metadata = _get_metadata(issue)
            if metadata is not None:
                message += metadata

        Notify.Notification.new("Bugwarrior", message, logo_path).show()