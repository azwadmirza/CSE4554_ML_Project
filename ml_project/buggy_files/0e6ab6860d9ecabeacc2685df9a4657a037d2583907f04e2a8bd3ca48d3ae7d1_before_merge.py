    def data_received(self, data):
        try:
            self.parser.feed_data(data)
        except httptools.HttpParserUpgrade:
            websocket_upgrade(self)