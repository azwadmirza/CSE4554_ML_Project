        def on_request_error(failure):
            failure.trap(SchemeNotSupported, ConnectError, DNSLookupError)
            self._logger.error("Error when performing version check request: %s", failure)