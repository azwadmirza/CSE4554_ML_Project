def http_get(uri):

    def _on_response(response):
        if response.code == http.OK:
            return readBody(response)
        raise HttpError(response)

    treq_deferred = treq.get(uri, persistent=False)
    treq_deferred.addCallback(_on_response)
    return treq_deferred