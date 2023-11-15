def notify_download(ep_name):
    for n in notifiers:
        try:
            n.notify_download(ep_name)
        except (RequestException, socket.gaierror) as e:
            logger.debug(u'Unable to send download notification. Error: {error}', error=e.message)