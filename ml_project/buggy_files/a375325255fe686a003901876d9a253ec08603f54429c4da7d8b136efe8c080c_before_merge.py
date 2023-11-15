def http_get(uri):
    """
    Performs a GET request
    :param uri: The URL to perform a GET request to
    :return: A deferred firing the body of the response.
    :raises HttpError: When the HTTP response code is not OK (i.e. not the HTTP Code 200)
    """
    def _on_response(response):
        if response.code == http.OK:
            return readBody(response)
        if response.code == http.FOUND:
            # Check if location header contains magnet link
            location_headers = response.headers.getRawHeaders("location")
            if not location_headers:
                return fail(Failure(RuntimeError("HTTP redirect response does not contain location header")))
            new_uri = location_headers[0]
            if new_uri.startswith('magnet'):
                _, infohash, _ = parse_magnetlink(new_uri)
                if infohash:
                    return succeed(new_uri)
            return http_get(new_uri)
        raise HttpError(response)

    try:
        uri = six.ensure_binary(uri)
    except AttributeError:
        pass
    try:
        contextFactory = WebClientContextFactory()
        agent = Agent(reactor, contextFactory)
        headers = Headers({'User-Agent': ['Tribler ' + version_id]})
        deferred = agent.request(b'GET', uri, headers, None)
        deferred.addCallback(_on_response)
        return deferred
    except:
        return fail()