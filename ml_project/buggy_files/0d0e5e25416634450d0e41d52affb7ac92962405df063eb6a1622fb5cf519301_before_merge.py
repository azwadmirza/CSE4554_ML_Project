def notify_git_update(new_version=""):
    for n in notifiers:
        if app.NOTIFY_ON_UPDATE:
            n.notify_git_update(new_version)