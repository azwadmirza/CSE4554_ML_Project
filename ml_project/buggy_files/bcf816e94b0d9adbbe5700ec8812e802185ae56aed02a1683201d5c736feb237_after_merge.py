    def __init__(self, endpoint, cacert=None, debug=False):
        self._url = httpclient.get_url_without_trailing_slash(endpoint) + '/stream'
        self.debug = debug
        self.cacert = cacert