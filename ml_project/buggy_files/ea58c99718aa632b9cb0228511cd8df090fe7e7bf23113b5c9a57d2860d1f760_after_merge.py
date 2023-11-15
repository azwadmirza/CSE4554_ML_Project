        def on_error(error):
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.write(json.dumps({"error": unichar_string(error.getErrorMessage())}))
            request.finish()