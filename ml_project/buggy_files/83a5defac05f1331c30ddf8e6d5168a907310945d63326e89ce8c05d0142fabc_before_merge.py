    def bind_socket(self):
        family, sockettype, proto, canonname, sockaddr = socket.getaddrinfo(
            self.host, self.port, type=socket.SOCK_STREAM
        )[0]
        sock = socket.socket(family=family, type=sockettype)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
        except OSError as exc:
            logger.error(exc)
            sys.exit(1)
        sock.set_inheritable(True)

        if family == socket.AddressFamily.AF_INET6:
            message, color_message = _get_server_start_message(_IPKind.IPv6)
        else:
            message, color_message = _get_server_start_message(_IPKind.IPv4)
        protocol_name = "https" if self.is_ssl else "http"
        logger.info(
            message,
            protocol_name,
            self.host,
            self.port,
            extra={"color_message": color_message},
        )
        return sock