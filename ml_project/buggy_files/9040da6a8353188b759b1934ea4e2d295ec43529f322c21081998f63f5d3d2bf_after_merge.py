    def render(self, request):
        """
        Render the resource. This will takeover the transport underlying
        the request, create a :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
        and let that do any subsequent communication.
        """
        # for reasons unknown, the transport is already None when the
        # request is over HTTP2. request.channel.getPeer() is valid at
        # this point however
        if request.channel.transport is None:
            # render an "error, you're doing HTTPS over WSS" webpage
            from autobahn.websocket import protocol
            request.setResponseCode(426, b"Upgrade required")
            # RFC says MUST set upgrade along with 426 code:
            # https://tools.ietf.org/html/rfc7231#section-6.5.15
            request.setHeader(b"Upgrade", b"WebSocket")
            html = protocol._SERVER_STATUS_TEMPLATE % ("", protocol.__version__)
            return html.encode('utf8')

        # Create Autobahn WebSocket protocol.
        #
        protocol = self._factory.buildProtocol(request.transport.getPeer())
        if not protocol:
            # If protocol creation fails, we signal "internal server error"
            request.setResponseCode(500)
            return b""

        # Take over the transport from Twisted Web
        #
        transport, request.channel.transport = request.channel.transport, None

        # Connect the transport to our protocol. Once #3204 is fixed, there
        # may be a cleaner way of doing this.
        # http://twistedmatrix.com/trac/ticket/3204
        #
        if isinstance(transport, ProtocolWrapper):
            # i.e. TLS is a wrapping protocol
            transport.wrappedProtocol = protocol
        else:
            transport.protocol = protocol
        protocol.makeConnection(transport)

        # On Twisted 16+, the transport is paused whilst the existing
        # request is served; there won't be any requests after us so
        # we can just resume this ourselves.
        # 17.1 version
        if hasattr(transport, "_networkProducer"):
            transport._networkProducer.resumeProducing()
        # 16.x version
        elif hasattr(transport, "resumeProducing"):
            transport.resumeProducing()

        # We recreate the request and forward the raw data. This is somewhat
        # silly (since Twisted Web already did the HTTP request parsing
        # which we will do a 2nd time), but it's totally non-invasive to our
        # code. Maybe improve this.
        #
        if PY3:

            data = request.method + b' ' + request.uri + b' HTTP/1.1\x0d\x0a'
            for h in request.requestHeaders.getAllRawHeaders():
                data += h[0] + b': ' + b",".join(h[1]) + b'\x0d\x0a'
            data += b"\x0d\x0a"
            data += request.content.read()

        else:
            data = "%s %s HTTP/1.1\x0d\x0a" % (request.method, request.uri)
            for h in request.requestHeaders.getAllRawHeaders():
                data += "%s: %s\x0d\x0a" % (h[0], ",".join(h[1]))
            data += "\x0d\x0a"
        protocol.dataReceived(data)

        return NOT_DONE_YET