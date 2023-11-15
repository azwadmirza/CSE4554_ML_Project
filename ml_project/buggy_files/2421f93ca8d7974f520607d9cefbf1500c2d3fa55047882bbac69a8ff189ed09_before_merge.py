    def handle(self):
        self.log("clientconnect", "info")

        root_layer = self._create_root_layer()
        root_layer = self.channel.ask("clientconnect", root_layer)
        if root_layer == Kill:
            def root_layer():
                raise Kill()

        try:
            root_layer()
        except Kill:
            self.log("Connection killed", "info")
        except ProtocolException as e:

            if isinstance(e, ClientHandshakeException):
                self.log(
                    "Client Handshake failed. "
                    "The client may not trust the proxy's certificate for {}.".format(e.server),
                    "error"
                )
                self.log(repr(e), "debug")
            else:
                self.log(repr(e), "info")

                self.log(traceback.format_exc(), "debug")
            # If an error propagates to the topmost level,
            # we send an HTTP error response, which is both
            # understandable by HTTP clients and humans.
            try:
                error_response = make_error_response(502, repr(e))
                self.client_conn.send(assemble_response(error_response))
            except TcpException:
                pass
        except Exception:
            self.log(traceback.format_exc(), "error")
            print(traceback.format_exc(), file=sys.stderr)
            print("mitmproxy has crashed!", file=sys.stderr)
            print("Please lodge a bug report at: https://github.com/mitmproxy/mitmproxy", file=sys.stderr)

        self.log("clientdisconnect", "info")
        self.channel.tell("clientdisconnect", root_layer)
        self.client_conn.finish()