    def connect(self) -> None:
        try:
            parsed_url = urlparse(self.url.strip())
            hostname: str = parsed_url.hostname
            port: int = parsed_url.port or (443 if parsed_url.scheme == "wss" else 80)
            if self.trace_enabled:
                self.logger.debug(
                    f"Connecting to the address for handshake: {hostname}:{port} "
                    f"(session id: {self.session_id})"
                )
            sock: Union[ssl.SSLSocket, socket] = _establish_new_socket_connection(
                session_id=self.session_id,
                server_hostname=hostname,
                server_port=port,
                logger=self.logger,
                receive_timeout=self.receive_timeout,
                proxy=self.proxy,
                proxy_headers=self.proxy_headers,
                trace_enabled=self.trace_enabled,
            )

            # WebSocket handshake
            try:
                path = f"{parsed_url.path}?{parsed_url.query}"
                sec_websocket_key = _generate_sec_websocket_key()
                message = f"""GET {path} HTTP/1.1
                    Host: {parsed_url.hostname}
                    Upgrade: websocket
                    Connection: Upgrade
                    Sec-WebSocket-Key: {sec_websocket_key}
                    Sec-WebSocket-Version: 13

                """
                req: str = "\r\n".join([line.lstrip() for line in message.split("\n")])
                if self.trace_enabled:
                    self.logger.debug(
                        f"{self.connection_type_name} handshake request (session id: {self.session_id}):\n{req}"
                    )
                sock.send(req.encode("utf-8"))
                sock.settimeout(self.receive_timeout)
                status, headers, text = _parse_handshake_response(sock)
                if self.trace_enabled:
                    self.logger.debug(
                        f"{self.connection_type_name} handshake response (session id: {self.session_id}):\n{text}"
                    )
                # HTTP/1.1 101 Switching Protocols
                if status == 101:
                    if not _validate_sec_websocket_accept(sec_websocket_key, headers):
                        raise SlackClientNotConnectedError(
                            f"Invalid response header detected in {self.connection_type_name} handshake response"
                            f" (session id: {self.session_id})"
                        )
                    # set this successfully connected socket
                    self.sock = sock
                    self.ping(f"{self.session_id}:{time.time()}")
                else:
                    message = (
                        f"Received an unexpected response for handshake "
                        f"(status: {status}, response: {text}, session id: {self.session_id})"
                    )
                    self.logger.warning(message)

            except socket.error as e:
                code: Optional[int] = None
                if e.args and len(e.args) > 1 and isinstance(e.args[0], int):
                    code = e.args[0]
                if code is not None:
                    self.logger.exception(
                        f"Error code: {code} (session id: {self.session_id}, error: {e})"
                    )
                raise

        except Exception as e:
            self.logger.exception(
                f"Failed to establish a connection (session id: {self.session_id}, error: {e})"
            )
            self.disconnect()