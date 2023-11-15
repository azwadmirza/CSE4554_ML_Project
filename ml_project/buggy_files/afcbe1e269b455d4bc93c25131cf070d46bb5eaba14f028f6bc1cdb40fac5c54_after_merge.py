def notify_login(ipaddress):
    for n in notifiers:
        if app.NOTIFY_ON_LOGIN:
            try:
                n.notify_login(ipaddress)
            except (RequestException, socket.gaierror) as e:
                logger.debug(u'Unable to new login notification. Error: {error}', error=e.message)