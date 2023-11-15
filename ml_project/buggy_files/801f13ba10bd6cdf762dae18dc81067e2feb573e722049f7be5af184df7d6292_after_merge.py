    def _password_auth(self):
        try:
            self.session.userauth_password(self.user, self.password)
        except Exception as ex:
            raise AuthenticationError("Password authentication failed - %s", ex)