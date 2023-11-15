        def on_request_error(failure):
            request.setResponseCode(http.BAD_REQUEST)
            request.write(json.dumps({"error": failure.getErrorMessage()}))
            self.finish_request(request)