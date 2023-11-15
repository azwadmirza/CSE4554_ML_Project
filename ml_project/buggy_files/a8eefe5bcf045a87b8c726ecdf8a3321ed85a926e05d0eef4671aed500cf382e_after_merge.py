    def send_push(self, task, api_key, title, body, url=None, destination=None, destination_type=None):

        if url:
            push_type = 'link'
        else:
            push_type = 'note'

        data = {'type': push_type, 'title': title, 'body': body}
        if url:
            data['url'] = url
        if destination:
            data[destination_type] = destination

        # Check for test mode
        if task.options.test:
            log.info('Test mode. Pushbullet notification would be:')
            log.info('    API Key: %s' % api_key)
            log.info('    Type: %s' % push_type)
            log.info('    Title: %s' % title)
            log.info('    Body: %s' % body)
            if destination:
                log.info('    Destination: %s (%s)' % (destination, destination_type))
            if url:
                log.info('    URL: %s' % url)
            log.info('    Raw Data: %s' % json.dumps(data))
            # Test mode.  Skip remainder.
            return

        # Make the request
        headers = {
            'Authorization': 'Basic %s' % base64.b64encode(api_key.encode('ascii')),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Flexget'
        }
        response = task.requests.post(pushbullet_url, headers=headers, data=json.dumps(data), raise_status=False)

        # Check if it succeeded
        request_status = response.status_code

        # error codes and messages from Pushbullet API
        if request_status == 200:
            log.debug('Pushbullet notification sent')
        elif request_status == 500:
            log.warning('Pushbullet notification failed, Pushbullet API having issues')
            # TODO: Implement retrying. API requests 5 seconds between retries.
        elif request_status >= 400:
            if response.content:
                try:
                    error = json.loads(response.content)['error']
                except ValueError:
                    error = 'Unknown Error (Invalid JSON returned)'
            log.error('Pushbullet API error: %s' % error['message'])
        else:
            log.error('Unknown error when sending Pushbullet notification')