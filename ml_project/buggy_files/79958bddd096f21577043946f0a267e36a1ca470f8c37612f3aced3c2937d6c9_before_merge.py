    def get_request(self, uri, parse_json_result=True, headers=None, get_only=False, fail_on_error=True):
        '''
        Perform a GET-like request. Will try POST-as-GET for ACMEv2, with fallback
        to GET if server replies with a status code of 405.
        '''
        if not get_only and self.version != 1:
            # Try POST-as-GET
            content, info = self.send_signed_request(uri, None, parse_json_result=False)
            if info['status'] == 405:
                # Instead, do unauthenticated GET
                get_only = True
        else:
            # Do unauthenticated GET
            get_only = True

        if get_only:
            # Perform unauthenticated GET
            resp, info = fetch_url(self.module, uri, method='GET', headers=headers)

            try:
                content = resp.read()
            except AttributeError:
                content = info.pop('body', None)

        # Process result
        if parse_json_result:
            result = {}
            if content:
                if info['content-type'].startswith('application/json'):
                    try:
                        result = self.module.from_json(content.decode('utf8'))
                    except ValueError:
                        raise ModuleFailException("Failed to parse the ACME response: {0} {1}".format(uri, content))
                else:
                    result = content
        else:
            result = content

        if fail_on_error and info['status'] >= 400:
            raise ModuleFailException("ACME request failed: CODE: {0} RESULT: {1}".format(info['status'], result))
        return result, info