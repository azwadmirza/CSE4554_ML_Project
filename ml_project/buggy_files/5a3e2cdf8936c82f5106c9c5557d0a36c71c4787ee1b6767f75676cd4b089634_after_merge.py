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

        for tries in range(5):
            for file in files:
                file.reset(seek=tries)

            r = self.session.request(verb, url, headers=headers, data=data, files=multipart)
            r.encoding = 'utf-8'
            # Coerce empty responses to return None for hygiene purposes
            response = r.text or None

            # compatibility with aiohttp
            r.status = r.status_code

            if r.headers['Content-Type'] == 'application/json':
                response = json.loads(response)

            # check if we have rate limit header information
            remaining = r.headers.get('X-Ratelimit-Remaining')
            if remaining == '0' and r.status != 429 and self.sleep:
                delta = utils._parse_ratelimit_header(r)
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