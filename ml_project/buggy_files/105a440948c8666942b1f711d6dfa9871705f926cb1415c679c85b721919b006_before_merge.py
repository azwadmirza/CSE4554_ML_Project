        def on_metainfo_timeout(_):
            request.setResponseCode(http.REQUEST_TIMEOUT)
            request.write(json.dumps({"error": "timeout"}))
            self.finish_request(request)