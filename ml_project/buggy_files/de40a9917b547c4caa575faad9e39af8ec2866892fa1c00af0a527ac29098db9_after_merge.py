    def prepare(self) -> None:
        for key, value in self.stream.get_headers().items():
            # Ignore Transfer-Encoding if the Content-Length has been set explicitly.
            if key.lower() == "transfer-encoding" and "content-length" in self.headers:
                continue
            self.headers.setdefault(key, value)

        auto_headers: typing.List[typing.Tuple[bytes, bytes]] = []

        has_host = "host" in self.headers
        has_content_length = (
            "content-length" in self.headers or "transfer-encoding" in self.headers
        )
        has_user_agent = "user-agent" in self.headers
        has_accept = "accept" in self.headers
        has_accept_encoding = "accept-encoding" in self.headers
        has_connection = "connection" in self.headers

        if not has_host:
            url = self.url
            if url.userinfo:
                url = url.copy_with(username=None, password=None)
            auto_headers.append((b"host", url.authority.encode("ascii")))
        if not has_content_length and self.method in ("POST", "PUT", "PATCH"):
            auto_headers.append((b"content-length", b"0"))
        if not has_user_agent:
            auto_headers.append((b"user-agent", USER_AGENT.encode("ascii")))
        if not has_accept:
            auto_headers.append((b"accept", b"*/*"))
        if not has_accept_encoding:
            auto_headers.append((b"accept-encoding", ACCEPT_ENCODING.encode()))
        if not has_connection:
            auto_headers.append((b"connection", b"keep-alive"))

        self.headers = Headers(auto_headers + self.headers.raw)