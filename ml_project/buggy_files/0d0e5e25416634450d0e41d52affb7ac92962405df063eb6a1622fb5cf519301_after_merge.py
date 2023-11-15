def notify_git_update(new_version=""):
    for n in notifiers:
        if app.NOTIFY_ON_UPDATE:
            try:
                n.notify_git_update(new_version)
            except (RequestException, socket.gaierror) as e:
                logger.debug(u'Unable to send new update notification. Error: {error}', error=e.message)