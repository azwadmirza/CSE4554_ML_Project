    async def request(self, verb, url, payload=None, multipart=None, *, files=None, reason=None):
        headers = {}
        data = None
        files = files or []
        if payload:
            headers['Content-Type'] = 'application/json'
            data = utils.to_json(payload)
        
        if reason:
            headers['X-Audit-Log-Reason'] = _uriquote(reason, safe='/ ')

        if multipart:
            data = aiohttp.FormData()
            for key, value in multipart.items():
                if key.startswith('file'):
                    data.add_field(key, value[1], filename=value[0], content_type=value[2])
                else:
                    data.add_field(key, value)

        for tries in range(5):
            for file in files:
                file.reset(seek=tries)

            async with self.session.request(verb, url, headers=headers, data=data) as r:
                # Coerce empty strings to return None for hygiene purposes
                response = (await r.text(encoding='utf-8')) or None
                if r.headers['Content-Type'] == 'application/json':
                    response = json.loads(response)

                # check if we have rate limit header information
                remaining = r.headers.get('X-Ratelimit-Remaining')
                if remaining == '0' and r.status != 429:
                    delta = utils._parse_ratelimit_header(r)
                    await asyncio.sleep(delta)

                if 300 > r.status >= 200:
                    return response

                # we are being rate limited
                if r.status == 429:
                    if not r.headers.get('Via'):
                        # Banned by Cloudflare more than likely.
                        raise HTTPException(r, data)

                    retry_after = response['retry_after'] / 1000.0
                    await asyncio.sleep(retry_after)
                    continue

                if r.status in (500, 502):
                    await asyncio.sleep(1 + tries * 2)
                    continue

                if r.status == 403:
                    raise Forbidden(r, response)
                elif r.status == 404:
                    raise NotFound(r, response)
                else:
                    raise HTTPException(r, response)
        # no more retries
        raise HTTPException(r, response)