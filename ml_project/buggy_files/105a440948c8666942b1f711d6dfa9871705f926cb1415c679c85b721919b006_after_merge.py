        def on_metainfo_timeout(_):
            if not request.finished:
                request.setResponseCode(http.REQUEST_TIMEOUT)
                request.write(json.dumps({"error": "timeout"}))
            # If the above request.write failed, the request will have already been finished
            if not request.finished:
                self.finish_request(request)