    def check_new_version(self):

        def parse_body(body):
            if body is None:
                return
            version = json.loads(body)['name'][1:]
            if LooseVersion(version) > LooseVersion(version_id):
                self.session.notifier.notify(NTFY_NEW_VERSION, NTFY_INSERT, None, version)

        def on_request_error(error):
            error.trap(SchemeNotSupported, ConnectError, DNSLookupError)
            self._logger.error("Error when performing version check request: %s", error)

        def parse_response(response):
            if response.code == 200:
                return readBody(response)
            else:
                self._logger.warning("Got response code %s when performing version check request", response.code)

        agent = Agent(reactor)
        return agent.request('GET', VERSION_CHECK_URL, Headers({'User-Agent': ['Tribler ' + version_id]}), None)\
            .addCallback(parse_response).addCallback(parse_body).addErrback(on_request_error)