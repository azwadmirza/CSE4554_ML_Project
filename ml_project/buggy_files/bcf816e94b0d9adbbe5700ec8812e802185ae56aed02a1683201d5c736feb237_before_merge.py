    def __init__(self, endpoint, cacert, debug):
        self._url = httpclient.get_url_without_trailing_slash(endpoint) + '/stream'
        self.debug = debug
        self.cacert = cacert