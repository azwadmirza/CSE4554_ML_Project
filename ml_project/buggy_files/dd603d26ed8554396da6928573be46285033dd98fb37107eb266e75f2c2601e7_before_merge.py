    def _check_authentication(self):
        """Check if JWT or API key is provided and valid."""
        if self.request.method == 'OPTIONS':
            return

        api_key = self.get_argument('api_key', default=None) or self.request.headers.get('X-Api-Key')
        if api_key and api_key == app.API_KEY:
            return

        authorization = self.request.headers.get('Authorization')
        if not authorization:
            return self._unauthorized('No authorization token.')

        if authorization.startswith('Bearer'):
            try:
                token = authorization.replace('Bearer ', '')
                jwt.decode(token, app.ENCRYPTION_SECRET, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return self._unauthorized('Token has expired.')
            except jwt.DecodeError:
                return self._unauthorized('Invalid token.')
        elif authorization.startswith('Basic'):
            auth_decoded = base64.decodestring(authorization[6:])
            username, password = auth_decoded.split(':', 2)
            if username != app.WEB_USERNAME or password != app.WEB_PASSWORD:
                return self._unauthorized('Invalid user/pass.')
        else:
            return self._unauthorized('Invalid token.')