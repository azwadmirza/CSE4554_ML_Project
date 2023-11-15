    def sni(self):
        for extension in self._client_hello.extensions.extensions:
            is_valid_sni_extension = (
                extension.type == 0x00 and
                len(extension.server_names) == 1 and
                extension.server_names[0].name_type == 0 and
                check.is_valid_host(extension.server_names[0].host_name)
            )
            if is_valid_sni_extension:
                return extension.server_names[0].host_name.decode("idna")