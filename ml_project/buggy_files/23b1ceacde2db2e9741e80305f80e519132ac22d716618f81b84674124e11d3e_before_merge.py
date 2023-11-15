    def load_flow(self, f):
        """
        Loads a flow
        """
        if isinstance(f, models.HTTPFlow):
            if self.server and self.options.mode == "reverse":
                f.request.host = self.server.config.upstream_server.address.host
                f.request.port = self.server.config.upstream_server.address.port
                f.request.scheme = self.server.config.upstream_server.scheme

            f.reply = controller.DummyReply()
            if f.request:
                self.request(f)
            if f.response:
                self.responseheaders(f)
                self.response(f)
            if f.error:
                self.error(f)
        elif isinstance(f, models.TCPFlow):
            messages = f.messages
            f.messages = []
            f.reply = controller.DummyReply()
            self.tcp_open(f)
            while messages:
                f.messages.append(messages.pop(0))
                self.tcp_message(f)
            if f.error:
                self.tcp_error(f)
            self.tcp_close(f)
        else:
            raise NotImplementedError()