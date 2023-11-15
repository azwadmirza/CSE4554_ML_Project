def call_hook(message,
              attachment=None,
              color='good',
              short=False,
              identifier=None,
              channel=None,
              username=None,
              icon_emoji=None):
    '''
    Send message to Slack incomming webhook.

    :param message:     The topic of message.
    :param attachment:  The message to send to the Slacke WebHook.
    :param color:       The color of border of left side
    :param short:       An optional flag indicating whether the value is short
                        enough to be displayed side-by-side with other values.
    :param identifier:  The identifier of WebHook.
    :param channel:     The channel to use instead of the WebHook default.
    :param username:    Username to use instead of WebHook default.
    :param icon_emoji:  Icon to use instead of WebHook default.
    :return:            Boolean if message was sent successfuly.

    CLI Example:

    .. code-block:: bash

        salt '*' slack.post_hook message='Hello, from SaltStack'

    '''
    base_url = 'https://hooks.slack.com/services/'
    if not identifier:
        identifier = _get_hook_id()

    url = _urljoin(base_url, identifier)

    if not message:
        log.error('message is required option')

    if attachment:
        payload = {
            'attachments': [
                {
                    'fallback': message,
                    'color': color,
                    'pretext': message,
                    'fields': [
                        {
                            "value": attachment,
                            "short": short,
                        }
                    ]
                }
            ]
        }
    else:
        payload = {
            'text': message,
        }

    if channel:
        payload['channel'] = channel

    if username:
        payload['username'] = username

    if icon_emoji:
        payload['icon_emoji'] = icon_emoji

    data = _urlencode(
        {
            'payload': json.dumps(payload, ensure_ascii=False)
        }
    )
    result = salt.utils.http.query(url, 'POST', data=data)

    if result['status'] <= 201:
        return True
    else:
        return {
            'res': False,
            'message': result.get('body', result['status'])
        }