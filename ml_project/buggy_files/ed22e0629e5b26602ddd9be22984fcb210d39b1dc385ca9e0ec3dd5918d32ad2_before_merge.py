def notify_download(ep_name):
    for n in notifiers:
        n.notify_download(ep_name)