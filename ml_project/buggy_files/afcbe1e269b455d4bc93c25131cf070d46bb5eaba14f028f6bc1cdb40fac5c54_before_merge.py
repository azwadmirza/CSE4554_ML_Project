def notify_login(ipaddress):
    for n in notifiers:
        if app.NOTIFY_ON_LOGIN:
            n.notify_login(ipaddress)