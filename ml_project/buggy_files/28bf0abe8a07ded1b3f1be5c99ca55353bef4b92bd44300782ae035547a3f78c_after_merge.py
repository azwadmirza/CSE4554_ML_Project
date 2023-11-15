    def load_from_url(url):
        """
        Load a BT .torrent or Tribler .tstream file from the URL and
        convert it into a TorrentDef.

        @param url URL
        @return Deferred
        """
        # Class method, no locking required
        def _on_response(data):
            return TorrentDef.load_from_memory(data)

        deferred = http_get(url)
        deferred.addCallback(_on_response)
        return deferred