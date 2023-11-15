    def make_connection(self, host):
        self.realhost = host
        h = six.moves.http_client.HTTP(self.proxy)
        return h