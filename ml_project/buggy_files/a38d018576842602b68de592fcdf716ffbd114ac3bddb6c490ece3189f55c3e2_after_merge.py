    def __call__(self):
        if self.mode == "transparent":
            self.__initial_server_tls = self._server_tls
            self.__initial_server_conn = self.server_conn
        while True:
            try:
                request = self.get_request_from_client()
                self.log("request", "debug", [repr(request)])

                # Handle Proxy Authentication
                # Proxy Authentication conceptually does not work in transparent mode.
                # We catch this misconfiguration on startup. Here, we sort out requests
                # after a successful CONNECT request (which do not need to be validated anymore)
                if self.mode != "transparent" and not self.authenticate(request):
                    return

                # Make sure that the incoming request matches our expectations
                self.validate_request(request)

                # Regular Proxy Mode: Handle CONNECT
                if self.mode == "regular" and request.first_line_format == "authority":
                    self.handle_regular_mode_connect(request)
                    return

            except HttpReadDisconnect:
                # don't throw an error for disconnects that happen before/between requests.
                return
            except NetlibException as e:
                self.send_error_response(400, repr(e))
                six.reraise(ProtocolException, ProtocolException(
                    "Error in HTTP connection: %s" % repr(e)), sys.exc_info()[2])

            try:
                flow = HTTPFlow(self.client_conn, self.server_conn, live=self)
                flow.request = request
                # set upstream auth
                if self.mode == "upstream" and self.config.upstream_auth is not None:
                    self.data.headers["Proxy-Authorization"] = self.config.upstream_auth
                self.process_request_hook(flow)

                if not flow.response:
                    self.establish_server_connection(flow)
                    self.get_response_from_server(flow)
                else:
                    # response was set by an inline script.
                    # we now need to emulate the responseheaders hook.
                    flow = self.channel.ask("responseheaders", flow)

                self.log("response", "debug", [repr(flow.response)])
                flow = self.channel.ask("response", flow)
                self.send_response_to_client(flow)

                if self.check_close_connection(flow):
                    return

                # Handle 101 Switching Protocols
                # It may be useful to pass additional args (such as the upgrade header)
                # to next_layer in the future
                if flow.response.status_code == 101:
                    layer = self.ctx.next_layer(self)
                    layer()
                    return

                # Upstream Proxy Mode: Handle CONNECT
                if flow.request.first_line_format == "authority" and flow.response.status_code == 200:
                    self.handle_upstream_mode_connect(flow.request.copy())
                    return

            except (ProtocolException, NetlibException) as e:
                self.send_error_response(502, repr(e))

                if not flow.response:
                    flow.error = Error(str(e))
                    self.channel.ask("error", flow)
                    self.log(traceback.format_exc(), "debug")
                    return
                else:
                    six.reraise(ProtocolException, ProtocolException(
                        "Error in HTTP connection: %s" % repr(e)), sys.exc_info()[2])
            finally:
                if flow:
                    flow.live = False