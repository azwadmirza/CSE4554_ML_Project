    def send_signed_request(self, url, payload, key_data=None, jws_header=None, parse_json_result=True, encode_payload=True):
        '''
        Sends a JWS signed HTTP POST request to the ACME server and returns
        the response as dictionary
        https://tools.ietf.org/html/rfc8555#section-6.2

        If payload is None, a POST-as-GET is performed.
        (https://tools.ietf.org/html/rfc8555#section-6.3)
        '''
        key_data = key_data or self.key_data
        jws_header = jws_header or self.jws_header
        failed_tries = 0
        while True:
            protected = copy.deepcopy(jws_header)
            protected["nonce"] = self.directory.get_nonce()
            if self.version != 1:
                protected["url"] = url

            self._log('URL', url)
            self._log('protected', protected)
            self._log('payload', payload)
            data = self.sign_request(protected, payload, key_data, encode_payload=encode_payload)
            if self.version == 1:
                data["header"] = jws_header.copy()
                for k, v in protected.items():
                    hv = data["header"].pop(k, None)
            self._log('signed request', data)
            data = self.module.jsonify(data)

            headers = {
                'Content-Type': 'application/jose+json',
            }
            resp, info = fetch_url(self.module, url, data=data, headers=headers, method='POST')
            _assert_fetch_url_success(resp, info)
            result = {}
            try:
                content = resp.read()
            except AttributeError:
                content = info.pop('body', None)

            if content or not parse_json_result:
                if (parse_json_result and info['content-type'].startswith('application/json')) or 400 <= info['status'] < 600:
                    try:
                        decoded_result = self.module.from_json(content.decode('utf8'))
                        self._log('parsed result', decoded_result)
                        # In case of badNonce error, try again (up to 5 times)
                        # (https://tools.ietf.org/html/rfc8555#section-6.7)
                        if (400 <= info['status'] < 600 and
                                decoded_result.get('type') == 'urn:ietf:params:acme:error:badNonce' and
                                failed_tries <= 5):
                            failed_tries += 1
                            continue
                        if parse_json_result:
                            result = decoded_result
                        else:
                            result = content
                    except ValueError:
                        raise ModuleFailException("Failed to parse the ACME response: {0} {1}".format(url, content))
                else:
                    result = content

            return result, info