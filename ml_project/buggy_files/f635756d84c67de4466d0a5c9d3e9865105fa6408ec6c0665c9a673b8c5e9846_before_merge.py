def http_get(uri):

    def _on_response(response):
        if response.code == http.OK:
            return readBody(response)
        raise HttpError(response)

    agent = Agent(reactor)
    deferred = agent.request(
        'GET',
        uri,
        Headers({'User-Agent': ['Tribler ' + version_id]}),
        None)
    deferred.addCallback(_on_response)
    return deferred