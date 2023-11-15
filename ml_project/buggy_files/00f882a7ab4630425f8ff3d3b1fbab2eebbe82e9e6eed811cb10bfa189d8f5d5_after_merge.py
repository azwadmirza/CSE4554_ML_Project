def notify_subtitle_download(ep_name, lang):
    for n in notifiers:
        try:
            n.notify_subtitle_download(ep_name, lang)
        except (RequestException, socket.gaierror) as e:
            logger.debug(u'Unable to send download notification. Error: {error}', error=e.message)