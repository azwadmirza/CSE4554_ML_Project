    async def _request_authentication(self):
        # https://dev.mysql.com/doc/internals/en/connection-phase-packets.html#packet-Protocol::HandshakeResponse
        if int(self.server_version.split('.', 1)[0]) >= 5:
            self.client_flag |= CLIENT.MULTI_RESULTS

        if self.user is None:
            raise ValueError("Did not specify a username")

        if self._ssl_context:
            # capablities, max packet, charset
            data = struct.pack('<IIB', self.client_flag, 16777216, 33)
            data += b'\x00' * (32 - len(data))

            self.write_packet(data)

            # Stop sending events to data_received
            self._writer.transport.pause_reading()

            # Get the raw socket from the transport
            raw_sock = self._writer.transport.get_extra_info('socket',
                                                             default=None)
            if raw_sock is None:
                raise RuntimeError("Transport does not expose socket instance")

            raw_sock = raw_sock.dup()
            self._writer.transport.close()
            # MySQL expects TLS negotiation to happen in the middle of a
            # TCP connection not at start. Passing in a socket to
            # open_connection will cause it to negotiate TLS on an existing
            # connection not initiate a new one.
            self._reader, self._writer = await asyncio.open_connection(
                sock=raw_sock, ssl=self._ssl_context, loop=self._loop,
                server_hostname=self._host
            )

        charset_id = charset_by_name(self.charset).id
        if isinstance(self.user, str):
            _user = self.user.encode(self.encoding)
        else:
            _user = self.user

        data_init = struct.pack('<iIB23s', self.client_flag, MAX_PACKET_LEN,
                                charset_id, b'')

        data = data_init + _user + b'\0'

        authresp = b''

        auth_plugin = self._client_auth_plugin
        if not self._client_auth_plugin:
            # Contains the auth plugin from handshake
            auth_plugin = self._server_auth_plugin

        if auth_plugin in ('', 'mysql_native_password'):
            authresp = _auth.scramble_native_password(
                self._password.encode('latin1'), self.salt)
        elif auth_plugin in ('', 'mysql_clear_password'):
            authresp = self._password.encode('latin1') + b'\0'

        if self.server_capabilities & CLIENT.PLUGIN_AUTH_LENENC_CLIENT_DATA:
            data += lenenc_int(len(authresp)) + authresp
        elif self.server_capabilities & CLIENT.SECURE_CONNECTION:
            data += struct.pack('B', len(authresp)) + authresp
        else:  # pragma: no cover
            # not testing against servers without secure auth (>=5.0)
            data += authresp + b'\0'

        if self._db and self.server_capabilities & CLIENT.CONNECT_WITH_DB:

            if isinstance(self._db, str):
                db = self._db.encode(self.encoding)
            else:
                db = self._db
            data += db + b'\0'

        if self.server_capabilities & CLIENT.PLUGIN_AUTH:
            name = auth_plugin
            if isinstance(name, str):
                name = name.encode('ascii')
            data += name + b'\0'

        self._auth_plugin_used = auth_plugin

        # Sends the server a few pieces of client info
        if self.server_capabilities & CLIENT.CONNECT_ATTRS:
            connect_attrs = b''
            for k, v in self._connect_attrs.items():
                k, v = k.encode('utf8'), v.encode('utf8')
                connect_attrs += struct.pack('B', len(k)) + k
                connect_attrs += struct.pack('B', len(v)) + v
            data += struct.pack('B', len(connect_attrs)) + connect_attrs

        self.write_packet(data)
        auth_packet = await self._read_packet()

        # if authentication method isn't accepted the first byte
        # will have the octet 254
        if auth_packet.is_auth_switch_request():
            # https://dev.mysql.com/doc/internals/en/
            # connection-phase-packets.html#packet-Protocol::AuthSwitchRequest
            auth_packet.read_uint8()  # 0xfe packet identifier
            plugin_name = auth_packet.read_string()
            if (self.server_capabilities & CLIENT.PLUGIN_AUTH and
                    plugin_name is not None):
                await self._process_auth(plugin_name, auth_packet)
            else:
                # send legacy handshake
                data = _auth.scramble_old_password(
                    self._password.encode('latin1'),
                    auth_packet.read_all()) + b'\0'
                self.write_packet(data)
                await self._read_packet()