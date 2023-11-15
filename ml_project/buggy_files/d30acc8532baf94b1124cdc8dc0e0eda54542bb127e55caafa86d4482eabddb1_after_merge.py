    def _perform_urllib_http_request(
        self, *, url: str, args: Dict[str, Dict[str, any]]
    ) -> Dict[str, any]:
        """Performs an HTTP request and parses the response.

        :param url: a complete URL (e.g., https://www.slack.com/api/chat.postMessage)
        :param args: args has "headers", "data", "params", and "json"
            "headers": Dict[str, str]
            "data": Dict[str, any]
            "params": Dict[str, str],
            "json": Dict[str, any],
        :return: dict {status: int, headers: Headers, body: str}
        """
        headers = args["headers"]
        if args["json"]:
            body = json.dumps(args["json"])
            headers["Content-Type"] = "application/json;charset=utf-8"
        elif args["data"]:
            boundary = f"--------------{uuid.uuid4()}"
            sep_boundary = b"\r\n--" + boundary.encode("ascii")
            end_boundary = sep_boundary + b"--\r\n"
            body = io.BytesIO()
            data = args["data"]
            for key, value in data.items():
                readable = getattr(value, "readable", None)
                if readable and value.readable():
                    filename = "Uploaded file"
                    name_attr = getattr(value, "name", None)
                    if name_attr:
                        filename = (
                            name_attr.decode("utf-8")
                            if isinstance(name_attr, bytes)
                            else name_attr
                        )
                    if "filename" in data:
                        filename = data["filename"]
                    mimetype = (
                        mimetypes.guess_type(filename)[0] or "application/octet-stream"
                    )
                    title = (
                        f'\r\nContent-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'
                        + f"Content-Type: {mimetype}\r\n"
                    )
                    value = value.read()
                else:
                    title = f'\r\nContent-Disposition: form-data; name="{key}"\r\n'
                    value = str(value).encode("utf-8")
                body.write(sep_boundary)
                body.write(title.encode("utf-8"))
                body.write(b"\r\n")
                body.write(value)

            body.write(end_boundary)
            body = body.getvalue()
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
            headers["Content-Length"] = len(body)
        elif args["params"]:
            body = urlencode(args["params"])
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = None

        if isinstance(body, str):
            body = body.encode("utf-8")

        # NOTE: Intentionally ignore the `http_verb` here
        # Slack APIs accepts any API method requests with POST methods
        try:
            # urllib not only opens http:// or https:// URLs, but also ftp:// and file://.
            # With this it might be possible to open local files on the executing machine
            # which might be a security risk if the URL to open can be manipulated by an external user.
            # (BAN-B310)
            if url.lower().startswith("http"):
                req = Request(method="POST", url=url, data=body, headers=headers)
                opener: Optional[OpenerDirector] = None
                if self.proxy is not None:
                    if isinstance(self.proxy, str):
                        opener = urllib.request.build_opener(
                            ProxyHandler({"http": self.proxy, "https": self.proxy}),
                            HTTPSHandler(context=self.ssl),
                        )
                    else:
                        raise SlackRequestError(
                            f"Invalid proxy detected: {self.proxy} must be a str value"
                        )

                # NOTE: BAN-B310 is already checked above
                resp: Optional[HTTPResponse] = None
                if opener:
                    resp = opener.open(req, timeout=self.timeout)  # skipcq: BAN-B310
                else:
                    resp = urlopen(  # skipcq: BAN-B310
                        req, context=self.ssl, timeout=self.timeout
                    )
                charset = resp.headers.get_content_charset()
                body: str = resp.read().decode(charset)  # read the response body here
                return {"status": resp.code, "headers": resp.headers, "body": body}
            raise SlackRequestError(f"Invalid URL detected: {url}")
        except HTTPError as e:
            resp = {"status": e.code, "headers": e.headers}
            if e.code == 429:
                # for compatibility with aiohttp
                resp["headers"]["Retry-After"] = resp["headers"]["retry-after"]

            charset = e.headers.get_content_charset()
            body: str = e.read().decode(charset)  # read the response body here
            resp["body"] = body
            return resp

        except Exception as err:
            self._logger.error(f"Failed to send a request to Slack API server: {err}")
            raise err