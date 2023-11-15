def add_station(uri):
    """Fetches the URI content and extracts IRFiles
    Returns None in error, else a possibly filled list of stations"""

    irfs = []
    if isinstance(uri, unicode):
        uri = uri.encode('utf-8')

    if uri.lower().endswith(".pls") or uri.lower().endswith(".m3u"):
        try:
            sock = urlopen(uri)
        except EnvironmentError as e:
            print_d("Got %s from %s" % (uri, e))
            encoding = util.get_locale_encoding()
            try:
                err = e.strerror.decode(encoding, 'replace')
            except TypeError:
                err = e.strerror[1].decode(encoding, 'replace')
            except AttributeError:
                # Give up and display the exception - may be useful HTTP info
                err = str(e)
            ErrorMessage(None, _("Unable to add station"), escape(err)).run()
            return None

        if uri.lower().endswith(".pls"):
            irfs = ParsePLS(sock)
        elif uri.lower().endswith(".m3u"):
            irfs = ParseM3U(sock)

        sock.close()
    else:
        try:
            irfs = [IRFile(uri)]
        except ValueError as err:
            ErrorMessage(None, _("Unable to add station"), err).run()

    return irfs