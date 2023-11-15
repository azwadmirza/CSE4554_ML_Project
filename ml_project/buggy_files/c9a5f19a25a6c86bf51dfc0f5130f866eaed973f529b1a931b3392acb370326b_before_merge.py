        def post(self, tag):  # pylint: disable=arguments-differ
            body = self.request.body
            headers = self.request.headers
            payload = {'headers': headers, 'body': body}
            fire('salt/engines/hook/' + tag, payload)