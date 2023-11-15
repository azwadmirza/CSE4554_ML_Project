    def _prepare_requests(self):
        """Created the TTS API the request(s) without sending them.

        Returns:
            list: ``requests.PreparedRequests_``. <https://2.python-requests.org/en/master/api/#requests.PreparedRequest>`_``.
        """
        # TTS API URL
        translate_url = _translate_url(tld=self.tld, path="_/TranslateWebserverUi/data/batchexecute")

        text_parts = self._tokenize(self.text)
        log.debug("text_parts: %i", len(text_parts))
        assert text_parts, 'No text to send to TTS API'

        prepared_requests = []
        for idx, part in enumerate(text_parts):
            data = self._package_rpc()

            log.debug("data-%i: %s", idx, data)

            # Request
            r = requests.Request(method='POST',
                                 url=translate_url,
                                 data=data,
                                 headers=self.GOOGLE_TTS_HEADERS)

            # Prepare request
            prepared_requests.append(r.prepare())

        return prepared_requests