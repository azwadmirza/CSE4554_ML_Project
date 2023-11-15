    def load_from_url(url):
        """
        If the URL starts with 'http:' load a BT .torrent or Tribler .tstream
        file from the URL and convert it into a TorrentDef. If the URL starts
        with our URL scheme, we convert the URL to a URL-compatible TorrentDef.

        If we can't download the .torrent file, this method returns None.

        @param url URL
        @return TorrentDef.
        """
        # Class method, no locking required
        try:
            # TODO Martijn: this request should be done using Twisted
            response = requests.get(url, timeout=30, verify=False)
            if response.ok:
                return TorrentDef.load_from_memory(response.content)

        except InvalidSchema:
            pass