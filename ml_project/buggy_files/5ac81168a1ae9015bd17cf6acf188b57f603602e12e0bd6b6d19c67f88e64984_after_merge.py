def notify_snatch(ep_name, is_proper):
    for n in notifiers:
        try:
            n.notify_snatch(ep_name, is_proper)
        except (RequestException, socket.gaierror) as e:
            logger.debug(u'Unable to send snatch notification. Error: {error}', error=e.message)