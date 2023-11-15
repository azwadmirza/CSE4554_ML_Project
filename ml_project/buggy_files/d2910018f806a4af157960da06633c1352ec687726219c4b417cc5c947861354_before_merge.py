    def _perform_http_request(
        self, *, body: Dict[str, any], headers: Dict[str, str]
    ) -> WebhookResponse:
        """Performs an HTTP request and parses the response.
        :param url: a complete URL to send data (e.g., https://hooks.slack.com/XXX)
        :param body: request body data
        :param headers: complete set of request headers
        :return: API response
        """
        body = json.dumps(body)
        headers["Content-Type"] = "application/json;charset=utf-8"

        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Sending a request - url: {self.url}, body: {body}, headers: {headers}"
            )
        try:
            url = self.url
            # for security (BAN-B310)
            if url.lower().startswith("http"):
                req = Request(
                    method="POST", url=url, data=body.encode("utf-8"), headers=headers
                )
                if self.proxy is not None:
                    host = re.sub("^https?://", "", self.proxy)
                    req.set_proxy(host, "http")
                    req.set_proxy(host, "https")
            else:
                raise SlackRequestError(f"Invalid URL detected: {url}")

            # NOTE: BAN-B310 is already checked above
            resp: HTTPResponse = urlopen(  # skipcq: BAN-B310
                req, context=self.ssl, timeout=self.timeout,
            )
            charset: str = resp.headers.get_content_charset() or "utf-8"
            response_body: str = resp.read().decode(charset)
            resp = WebhookResponse(
                url=url,
                status_code=resp.status,
                body=response_body,
                headers=resp.headers,
            )
            _debug_log_response(self.logger, resp)
            return resp

        except HTTPError as e:
            charset = e.headers.get_content_charset()
            body: str = e.read().decode(charset)  # read the response body here
            resp = WebhookResponse(
                url=url, status_code=e.code, body=body, headers=e.headers,
            )
            if e.code == 429:
                # for backward-compatibility with WebClient (v.2.5.0 or older)
                resp.headers["Retry-After"] = resp.headers["retry-after"]
            _debug_log_response(self.logger, resp)
            return resp

        except Exception as err:
            self.logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err