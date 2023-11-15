    def _get_json(self, url, data=None):
        if data:  # POST request
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            headers.update(self.custom_headers)
            response = self.requester.post(url, auth=self.auth, headers=headers,
                                           verify=self.VERIFY_SSL,
                                           stream=True,
                                           data=json.dumps(data))
        else:
            response = self.requester.get(url, auth=self.auth, headers=self.custom_headers,
                                          verify=self.VERIFY_SSL,
                                          stream=True)
        if response.status_code != 200: # Error message is text
            response.charset = "utf-8" # To be able to access ret.text (ret.content are bytes)
            raise get_exception_from_error(response.status_code)(response.text)

        return json.loads(decode_text(response.content))