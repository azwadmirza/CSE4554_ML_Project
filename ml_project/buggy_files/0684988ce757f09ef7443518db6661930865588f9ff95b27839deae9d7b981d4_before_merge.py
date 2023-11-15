def add_station(uri):
    """Fetches the URI content and extracts IRFiles"""

    irfs = []
    if isinstance(uri, unicode):
        uri = uri.encode('utf-8')

    if uri.lower().endswith(".pls") or uri.lower().endswith(".m3u"):
        try:
            sock = urlopen(uri)
        except EnvironmentError as e:
            encoding = util.get_locale_encoding()
            try:
                err = e.strerror.decode(encoding, 'replace')
            except (TypeError, AttributeError):
                err = e.strerror[1].decode(encoding, 'replace')
            qltk.ErrorMessage(None, _("Unable to add station"), err).run()
            return []

        if uri.lower().endswith(".pls"):
            irfs = ParsePLS(sock)
        elif uri.lower().endswith(".m3u"):
            irfs = ParseM3U(sock)

        sock.close()
    else:
        try:
            irfs = [IRFile(uri)]
        except ValueError as err:
            qltk.ErrorMessage(None, _("Unable to add station"), err).run()

    return irfs