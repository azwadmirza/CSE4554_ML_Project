        def post(self, tag):  # pylint: disable=arguments-differ
            body = self.request.body
            headers = self.request.headers
            payload = {
                'headers': headers if isinstance(headers, dict) else dict(headers),
                'body': body,
            }
            fire('salt/engines/hook/' + tag, payload)