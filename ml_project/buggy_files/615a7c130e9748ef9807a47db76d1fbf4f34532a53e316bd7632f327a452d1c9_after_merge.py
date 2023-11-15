    def check_new_version(self):

        def parse_body(body):
            if body is None:
                return
            version = json.loads(body)['name'][1:]
            if LooseVersion(version) > LooseVersion(version_id):
                self.session.notifier.notify(NTFY_NEW_VERSION, NTFY_INSERT, None, version)

        def on_request_error(failure):
            failure.trap(SchemeNotSupported, ConnectError, DNSLookupError)
            self._logger.error("Error when performing version check request: %s", failure)

        def on_response_error(failure):
            failure.trap(HttpError)
            self._logger.warning("Got response code %s when performing version check request",
                                 failure.value.response.code)

        deferred = http_get(VERSION_CHECK_URL)
        deferred.addErrback(on_response_error).addCallback(parse_body).addErrback(on_request_error)
        return deferred