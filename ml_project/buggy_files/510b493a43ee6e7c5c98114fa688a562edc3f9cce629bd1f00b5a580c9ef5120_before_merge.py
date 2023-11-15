    def handshake(self):
        global HARDCODED_PASSWORD, HARDCODED_USER

        def switch_auth(method='mysql_native_password'):
            self.packet(SwitchOutPacket, seed=self.salt, method=method).send()
            switch_out_answer = self.packet(SwitchOutResponse)
            switch_out_answer.get()
            return switch_out_answer.enc_password.value

        if self.session is None:
            self.initSession()
        log.info('send HandshakePacket')
        self.packet(HandshakePacket).send()

        handshake_resp = self.packet(HandshakeResponsePacket)
        handshake_resp.get()
        if handshake_resp.length == 0:
            log.warning('HandshakeResponsePacket empty')
            self.packet(OkPacket).send()
            return False
        self.client_capabilities = ClentCapabilities(handshake_resp.capabilities.value)

        client_auth_plugin = handshake_resp.client_auth_plugin.value.decode()

        orig_username = HARDCODED_USER
        orig_password = HARDCODED_PASSWORD
        orig_password_hash = handshake_resp.scramble_func(HARDCODED_PASSWORD, self.salt)
        username = None
        password = None

        self.session.is_ssl = False

        if handshake_resp.type == 'SSLRequest':
            log.info('switch to SSL')
            self.session.is_ssl = True
            ssl_socket = ssl.wrap_socket(
                self.socket,
                server_side=True,
                certfile=CERT_PATH,
                do_handshake_on_connect=True
            )
            self.socket = ssl_socket
            handshake_resp = self.packet(HandshakeResponsePacket)
            handshake_resp.get()
            client_auth_plugin = handshake_resp.client_auth_plugin.value.decode()
        
        username = handshake_resp.username.value.decode()

        if orig_username == username and HARDCODED_PASSWORD == '':
            log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
                'empty password')
            password = ''

        elif (DEFAULT_AUTH_METHOD not in client_auth_plugin) or \
            self.session.is_ssl is False and 'caching_sha2_password' in client_auth_plugin:
            new_method = 'caching_sha2_password' if 'caching_sha2_password' in client_auth_plugin else 'mysql_native_password'
    
            if new_method == 'caching_sha2_password' and self.session.is_ssl is False:
                log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
                    'error: cant switch to caching_sha2_password without SSL')
                self.packet(ErrPacket, err_code=ERR.ER_PASSWORD_NO_MATCH, msg=f'caching_sha2_password without SSL not supported').send()
                return False

            log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
                f'switch auth method to {new_method}')
            password = switch_auth(new_method)

            if new_method == 'caching_sha2_password':
                self.packet(FastAuthFail).send()
                password_answer = self.packet(PasswordAnswer)
                password_answer.get()
                password = password_answer.password.value.decode()
            else:
                orig_password = orig_password_hash

        elif 'caching_sha2_password' in client_auth_plugin:
            self.packet(FastAuthFail).send()
            log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
                'check auth using caching_sha2_password')
            password_answer = self.packet(PasswordAnswer)
            password_answer.get()
            password = password_answer.password.value.decode()
            orig_password = HARDCODED_PASSWORD
            
        elif 'mysql_native_password' in client_auth_plugin:
            log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
                'check auth using mysql_native_password')
            password = handshake_resp.enc_password.value
            orig_password = orig_password_hash
        else:
            log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
                'unknown method, possible ERROR. Try to switch to mysql_native_password')
            password = switch_auth('mysql_native_password')
            orig_password = orig_password_hash

        try:
            self.session.database = handshake_resp.database.value.decode()
        except Exception:
            self.session.database = None
        log.info(f'Check auth, user={username}, ssl={self.session.is_ssl}, auth_method={client_auth_plugin}: '
            f'connecting to database {self.session.database}')

        if self.isAuthOk(username, orig_username, password, orig_password):
            self.packet(OkPacket).send()
            return True
        else:
            self.packet(ErrPacket, err_code=ERR.ER_PASSWORD_NO_MATCH, msg=f'Access denied for user {username}').send()
            log.warning('AUTH FAIL')
            return False