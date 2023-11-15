    def create(self, method: str, url: str) -> None:
        try:
            req = http.HTTPRequest.make(method.upper(), url)
        except ValueError as e:
            ctx.log.error(e)
            return
        c = connections.ClientConnection.make_dummy(("", 0))
        s = connections.ServerConnection.make_dummy((req.host, req.port))
        f = http.HTTPFlow(c, s)
        f.request = req
        f.request.headers["Host"] = req.host
        self.add([f])