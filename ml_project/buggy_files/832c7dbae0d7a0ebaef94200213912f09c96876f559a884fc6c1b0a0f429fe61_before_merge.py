        def on_request_error(error):
            error.trap(SchemeNotSupported, ConnectError, DNSLookupError)
            self._logger.error("Error when performing version check request: %s", error)