    def is_temp_failure(self, exc): #IGNORE:W0613
        if is_temp_network_error(exc) or isinstance(exc, ssl.SSLError):
            # We probably can't use the connection anymore, so use this
            # opportunity to reset it
            self.conn.reset()
            return True

        elif isinstance(exc, RequestError) and (
                500 <= exc.code <= 599 or exc.code == 408):
            return True

        elif isinstance(exc, AccessTokenExpired):
            return True

        # Not clear at all what is happening here, but in doubt we retry
        elif isinstance(exc, ServerResponseError):
            return True

        if g_auth and isinstance(exc, g_auth.exceptions.TransportError):
            return True

        return False