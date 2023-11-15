def event(method, data=None, sender=None, hexlify=False):

    ''' Data is a dictionary.
    '''
    data = data or {}
    sender = sender or "plugin.video.jellyfin"

    if hexlify:
        data = '\\"[\\"{0}\\"]\\"'.format(binascii.hexlify(json.dumps(data)))
    else:
        data = '"[%s]"' % json.dumps(data).replace('"', '\\"')

    xbmc.executebuiltin('NotifyAll(%s, %s, %s)' % (sender, method, data))
    LOG.debug("---[ event: %s/%s ] %s", sender, method, data)