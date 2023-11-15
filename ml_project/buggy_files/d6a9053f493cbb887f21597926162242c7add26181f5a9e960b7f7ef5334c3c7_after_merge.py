    def __init__(self, url):
        p = urlparse(url)
        stripped = p._replace(params=None, query=None, fragment=None)
        super().__init__(stripped.geturl())
        self.params = p.params
        self.query = p.query
        self.fragment = p.fragment