def event(method, data=None, sender=None, hexlify=False):

    ''' Data is a dictionary.
    '''
    data = data or {}
    sender = sender or "plugin.video.jellyfin"

    if hexlify:
        data = ensure_text(binascii.hexlify(ensure_binary(json.dumps(data))))

    data = '"[%s]"' % json.dumps(data).replace('"', '\\"')

    LOG.debug("---[ event: %s/%s ] %s", sender, method, data)

    xbmc.executebuiltin('NotifyAll(%s, %s, %s)' % (sender, method, data))