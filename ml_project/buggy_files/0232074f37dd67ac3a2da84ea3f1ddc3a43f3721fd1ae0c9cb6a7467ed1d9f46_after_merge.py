    def handle_regular_connect(self, f):
        self.connect_request = True

        try:
            self.set_server((f.request.host, f.request.port))

            if f.response:
                resp = f.response
            else:
                resp = http.make_connect_response(f.request.data.http_version)

            self.send_response(resp)

            if is_ok(resp.status_code):
                layer = self.ctx.next_layer(self)
                layer()
        except (
            exceptions.ProtocolException, exceptions.NetlibException
        ) as e:
            # HTTPS tasting means that ordinary errors like resolution
            # and connection errors can happen here.
            self.send_error_response(502, repr(e))
            f.error = flow.Error(str(e))
            self.channel.ask("error", f)
            return False

        return False