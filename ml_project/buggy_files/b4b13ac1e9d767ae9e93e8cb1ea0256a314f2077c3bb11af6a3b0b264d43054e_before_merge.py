        def on_lookup_error(failure):
            failure.trap(ConnectError, DNSLookupError)
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.write(json.dumps({"error": failure.getErrorMessage()}))
            self.finish_request(request)