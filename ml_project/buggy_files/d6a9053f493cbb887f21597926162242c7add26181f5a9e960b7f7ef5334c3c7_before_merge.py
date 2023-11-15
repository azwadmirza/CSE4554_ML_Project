    def __init__(self, url):
        p = urlparse(url)
        assert not p.query and not p.params and not p.fragment
        assert p.password is None

        self.fill_parts(p.scheme, p.hostname, p.username, p.port, p.path)