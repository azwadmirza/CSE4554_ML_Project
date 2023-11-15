    def pull_data(self) -> Dict:
        """Pulls data from the server and returns the response dict

        Returns None if there is no DB saved in the server.

        Raises RemoteError if there are problems reaching the server or if
        there is an error returned by the server
        """
        signature, data = self.sign('get_saved_data')
        self.session.headers.update({
            'API-SIGN': base64.b64encode(signature.digest()),  # type: ignore
        })

        try:
            response = self.session.get(
                self.uri + 'get_saved_data',
                data=data,
                timeout=ROTKEHLCHEN_SERVER_TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            raise RemoteError('Could not connect to rotki server')

        return _process_dict_response(response)