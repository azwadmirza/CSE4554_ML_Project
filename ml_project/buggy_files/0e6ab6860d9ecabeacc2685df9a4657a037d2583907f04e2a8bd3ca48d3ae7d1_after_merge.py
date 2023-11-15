    def data_received(self, data):
        try:
            self.parser.feed_data(data)
        except httptools.parser.errors.HttpParserError:
            msg = "Invalid HTTP request received."
            self.logger.warn(msg)
            self.transport.close()
        except httptools.HttpParserUpgrade:
            websocket_upgrade(self)