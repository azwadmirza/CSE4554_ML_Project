    def _send_slack(self, message=None, webhook=None):
        """Send the http request using the Slack webhook."""
        webhook = webhook or app.SLACK_WEBHOOK

        log.info('Sending slack message: {message}', {'message': message})
        log.info('Sending slack message  to url: {url}', {'url': webhook})

        headers = {'Content-Type': 'application/json'}
        data = {
            'text': message,
            'username': 'MedusaBot',
            'icon_url': 'https://cdn.pymedusa.com/images/ico/favicon-310.png'
        }

        try:
            r = requests.post(webhook, data=json.dumps(data), headers=headers)
            r.raise_for_status()
        except Exception:
            log.exception('Error Sending Slack message')
            return False

        return True