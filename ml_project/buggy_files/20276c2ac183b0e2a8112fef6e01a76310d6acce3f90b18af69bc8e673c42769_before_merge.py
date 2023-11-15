    def send_push(self, api_key, title, body, url=None, destination=None, destination_type=None):
        push_type = 'link' if url else 'note'
        notification = {'type': push_type, 'title': title, 'body': body}
        if url:
            notification['url'] = url
        if destination:
            notification[destination_type] = destination

        # Make the request
        headers = {
            'Authorization': b'Basic ' + base64.b64encode(api_key.encode('ascii')),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Flexget',
        }
        try:
            response = requests.post(PUSHBULLET_URL, headers=headers, json=notification)
        except RequestException as e:
            if e.response is not None:
                if e.response.status_code == 429:
                    reset_time = datetime.datetime.fromtimestamp(
                        int(e.response.headers['X-Ratelimit-Reset'])
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    message = (
                        'Monthly Pushbullet database operations limit reached. Next reset: %s'
                        % reset_time
                    )
                else:
                    message = e.response.json()['error']['message']
            else:
                message = str(e)
            raise PluginWarning(message)

        reset_time = datetime.datetime.fromtimestamp(
            int(response.headers['X-Ratelimit-Reset'])
        ).strftime('%Y-%m-%d %H:%M:%S')
        remaining = response.headers['X-Ratelimit-Remaining']
        log.debug(
            'Pushbullet notification sent. Database operations remaining until next reset: %s. '
            'Next reset at: %s',
            remaining,
            reset_time,
        )