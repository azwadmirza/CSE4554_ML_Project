    def send_push(api_key, title, body, url=None, destination=None, destination_type=None):
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
                    reset_time = e.response.headers.get('X-Ratelimit-Reset')
                    if reset_time:
                        reset_time = datetime.datetime.fromtimestamp(int(reset_time)).strftime(
                            '%Y-%m-%d %H:%M:%S'
                        )
                        message = f'Monthly Pushbullet database operations limit reached. Next reset: {reset_time}'
                else:
                    message = e.response.json()['error']['message']
            else:
                message = str(e)
            raise PluginWarning(message)

        reset_time = response.headers.get('X-Ratelimit-Reset')
        remaining = response.headers.get('X-Ratelimit-Remaining')
        if reset_time and remaining:
            reset_time = datetime.datetime.fromtimestamp(int(reset_time))
            log.debug(
                'Pushbullet notification sent. Database operations remaining until next reset: %s. '
                'Next reset at: %s',
                remaining,
                reset_time,
            )