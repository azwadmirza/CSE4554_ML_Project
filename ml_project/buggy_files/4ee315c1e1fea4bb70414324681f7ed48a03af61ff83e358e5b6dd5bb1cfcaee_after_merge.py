    def request(self, verb, url, payload=None, multipart=None, *, files=None, reason=None):
        headers = {}
        data = None
        files = files or []
        if payload:
            headers['Content-Type'] = 'application/json'
            data = utils.to_json(payload)

        if reason:
            headers['X-Audit-Log-Reason'] = _uriquote(reason, safe='/ ')

        if multipart is not None:
            data = {'payload_json': multipart.pop('payload_json')}

        base_url = url.replace(self._request_url, '/') or '/'
        _id = self._webhook_id
        for tries in range(5):
            for file in files:
                file.reset(seek=tries)

            r = self.session.request(verb, url, headers=headers, data=data, files=multipart)
            r.encoding = 'utf-8'
            # Coerce empty responses to return None for hygiene purposes
            response = r.text or None

            # compatibility with aiohttp
            r.status = r.status_code

            log.debug('Webhook ID %s with %s %s has returned status code %s', _id, verb, base_url, r.status)
            if r.headers['Content-Type'] == 'application/json':
                response = json.loads(response)

            # check if we have rate limit header information
            remaining = r.headers.get('X-Ratelimit-Remaining')
            if remaining == '0' and r.status != 429 and self.sleep:
                delta = utils._parse_ratelimit_header(r)
                log.debug('Webhook ID %s has been pre-emptively rate limited, waiting %.2f seconds', _id, delta)
                time.sleep(delta)

            if 300 > r.status >= 200:
                return response

            # we are being rate limited
            if r.status == 429:
                if self.sleep:
                    if not r.headers.get('Via'):
                        # Banned by Cloudflare more than likely.
                        raise HTTPException(r, data)

                    retry_after = response['retry_after'] / 1000.0
                    log.warning('Webhook ID %s is rate limited. Retrying in %.2f seconds', _id, retry_after)
                    time.sleep(retry_after)
                    continue
                else:
                    raise HTTPException(r, response)

            if self.sleep and r.status in (500, 502):
                time.sleep(1 + tries * 2)
                continue

            if r.status == 403:
                raise Forbidden(r, response)
            elif r.status == 404:
                raise NotFound(r, response)
            else:
                raise HTTPException(r, response)
        # no more retries
        raise HTTPException(r, response)