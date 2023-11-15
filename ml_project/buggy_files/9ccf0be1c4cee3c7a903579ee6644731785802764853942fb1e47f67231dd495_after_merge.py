    def redirect_headers(self, request: AsyncRequest, url: URL, method: str) -> Headers:
        """
        Return the headers that should be used for the redirect request.
        """
        headers = Headers(request.headers)

        if url.origin != request.url.origin:
            # Strip Authorization headers when responses are redirected away from
            # the origin.
            del headers["Authorization"]
            del headers["Host"]

        if method != request.method and method == "GET":
            # If we've switch to a 'GET' request, then strip any headers which
            # are only relevant to the request body.
            del headers["Content-Length"]
            del headers["Transfer-Encoding"]

        return headers