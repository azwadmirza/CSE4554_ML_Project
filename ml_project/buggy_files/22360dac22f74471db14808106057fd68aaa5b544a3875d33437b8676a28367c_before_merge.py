    def listen(self, events=None, **kwargs):
        # Late import to avoid very expensive in-direct import (~1 second) when this function is
        # not called / used
        from sseclient import SSEClient

        url = self._url
        query_params = {}

        if events and isinstance(events, six.string_types):
            events = [events]

        if 'token' in kwargs:
            query_params['x-auth-token'] = kwargs.get('token')

        if 'api_key' in kwargs:
            query_params['st2-api-key'] = kwargs.get('api_key')

        if events:
            query_params['events'] = ','.join(events)

        query_string = '?' + urllib.parse.urlencode(query_params)
        url = url + query_string

        for message in SSEClient(url):

            # If the execution on the API server takes too long, the message
            # can be empty. In this case, rerun the query.
            if not message.data:
                continue

            yield json.loads(message.data)