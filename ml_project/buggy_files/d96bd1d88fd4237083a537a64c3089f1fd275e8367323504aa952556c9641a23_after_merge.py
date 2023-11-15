    def find_embed(self, url, max_width=None):
        # Find provider
        endpoint = self._get_endpoint(url)
        if endpoint is None:
            raise EmbedNotFoundException

        # Work out params
        params = self.options.copy()
        params['url'] = url
        params['format'] = 'json'
        if max_width:
            params['maxwidth'] = max_width

        # Perform request
        request = Request(endpoint + '?' + urlencode(params))
        request.add_header('User-agent', 'Mozilla/5.0')
        try:
            r = urllib_request.urlopen(request)
            oembed = json.loads(r.read().decode('utf-8'))
        except (URLError, json.decoder.JSONDecodeError):
            raise EmbedNotFoundException

        # Convert photos into HTML
        if oembed['type'] == 'photo':
            html = '<img src="%s" alt="">' % (oembed['url'], )
        else:
            html = oembed.get('html')

        # Return embed as a dict
        return {
            'title': oembed['title'] if 'title' in oembed else '',
            'author_name': oembed['author_name'] if 'author_name' in oembed else '',
            'provider_name': oembed['provider_name'] if 'provider_name' in oembed else '',
            'type': oembed['type'],
            'thumbnail_url': oembed.get('thumbnail_url'),
            'width': oembed.get('width'),
            'height': oembed.get('height'),
            'html': html,
        }