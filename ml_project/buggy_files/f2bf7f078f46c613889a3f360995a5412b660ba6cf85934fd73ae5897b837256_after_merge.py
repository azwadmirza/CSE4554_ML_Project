    def auth(self):
        if self.gssapi_auth or (self.gssapi_server_identity or self.gssapi_client_identity):
            try:
                return self.session.userauth_gssapi()
            except Exception as ex:
                logger.error(
                    "GSSAPI authentication with server id %s and client id %s failed - %s",
                    self.gssapi_server_identity, self.gssapi_client_identity, ex)
        return super(SSHClient, self).auth()