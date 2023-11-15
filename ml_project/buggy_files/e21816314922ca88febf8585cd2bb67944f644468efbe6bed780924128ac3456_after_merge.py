    def _internal_call(self, method, url, payload, params):
        args = dict(params=params)
        if not url.startswith("http"):
            url = self.prefix + url
        headers = self._auth_headers()

        if "content_type" in args["params"]:
            headers["Content-Type"] = args["params"]["content_type"]
            del args["params"]["content_type"]
            if payload:
                args["data"] = payload
        else:
            headers["Content-Type"] = "application/json"
            if payload:
                args["data"] = json.dumps(payload)

        if self.language is not None:
            headers["Accept-Language"] = self.language

        logger.debug('Sending %s to %s with Headers: %s and Body: %r ',
                     method, url, headers, args.get('data'))

        try:
            response = self._session.request(
                method, url, headers=headers, proxies=self.proxies,
                timeout=self.requests_timeout, **args
            )

            response.raise_for_status()
            results = response.json()
        except requests.exceptions.HTTPError:
            try:
                msg = response.json()["error"]["message"]
            except (ValueError, KeyError):
                msg = "error"
            try:
                reason = response.json()["error"]["reason"]
            except (ValueError, KeyError):
                reason = None

            logger.error('HTTP Error for %s to %s returned %s due to %s',
                         method, url, response.status_code, msg)

            raise SpotifyException(
                response.status_code,
                -1,
                "%s:\n %s" % (response.url, msg),
                reason=reason,
                headers=response.headers,
            )
        except requests.exceptions.RetryError:
            logger.error('Max Retries reached')
            raise SpotifyException(
                599,
                -1,
                "%s:\n %s" % (response.url, "Max Retries"),
                headers=response.headers,
            )
        except ValueError:
            results = None

        logger.debug('RESULTS: %s', results)
        return results