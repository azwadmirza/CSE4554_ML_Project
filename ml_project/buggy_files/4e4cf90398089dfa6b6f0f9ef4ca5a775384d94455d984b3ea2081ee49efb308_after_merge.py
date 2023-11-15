    def alpn_protocols(self):
        if self._client_hello.extensions:
            for extension in self._client_hello.extensions.extensions:
                if extension.type == 0x10:
                    return list(extension.alpn_protocols)
        return []