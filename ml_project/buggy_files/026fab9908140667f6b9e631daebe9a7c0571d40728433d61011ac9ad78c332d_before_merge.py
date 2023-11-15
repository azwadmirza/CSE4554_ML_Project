    async def _process_auth(self, plugin_name, auth_packet):
        if plugin_name == b"mysql_native_password":
            # https://dev.mysql.com/doc/internals/en/
            # secure-password-authentication.html#packet-Authentication::
            # Native41
            data = _auth.scramble_native_password(
                self._password.encode('latin1'),
                auth_packet.read_all())
        elif plugin_name == b"mysql_old_password":
            # https://dev.mysql.com/doc/internals/en/
            # old-password-authentication.html
            data = _auth.scramble_old_password(self._password.encode('latin1'),
                                               auth_packet.read_all()) + b'\0'
        elif plugin_name == b"mysql_clear_password":
            # https://dev.mysql.com/doc/internals/en/
            # clear-text-authentication.html
            data = self._password.encode('latin1') + b'\0'
        else:
            raise OperationalError(
                2059, "Authentication plugin '%s' not configured" % plugin_name
            )

        self.write_packet(data)
        pkt = await self._read_packet()
        pkt.check_error()

        self._auth_plugin_used = plugin_name

        return pkt