    def __init__(self, message, on_ack=noop,
                 hostname=None, eventer=None, app=None,
                 connection_errors=None, request_dict=None,
                 task=None, on_reject=noop, body=None,
                 headers=None, decoded=False, utc=True,
                 maybe_make_aware=maybe_make_aware,
                 maybe_iso8601=maybe_iso8601, **opts):
        if headers is None:
            headers = message.headers
        if body is None:
            body = message.body
        self.app = app
        self.message = message
        self.body = body
        self.utc = utc
        self._decoded = decoded
        if decoded:
            self.content_type = self.content_encoding = None
        else:
            self.content_type, self.content_encoding = (
                message.content_type, message.content_encoding,
            )

        self.id = headers['id']
        type = self.type = self.name = headers['task']
        self.root_id = headers.get('root_id')
        self.parent_id = headers.get('parent_id')
        if 'shadow' in headers:
            self.name = headers['shadow'] or self.name
        timelimit = headers.get('timelimit', None)
        if timelimit:
            self.time_limits = timelimit
        self.argsrepr = headers.get('argsrepr', '')
        self.kwargsrepr = headers.get('kwargsrepr', '')
        self.on_ack = on_ack
        self.on_reject = on_reject
        self.hostname = hostname or gethostname()
        self.eventer = eventer
        self.connection_errors = connection_errors or ()
        self.task = task or self.app.tasks[type]

        # timezone means the message is timezone-aware, and the only timezone
        # supported at this point is UTC.
        eta = headers.get('eta')
        if eta is not None:
            try:
                eta = maybe_iso8601(eta)
            except (AttributeError, ValueError, TypeError) as exc:
                raise InvalidTaskError(
                    'invalid ETA value {0!r}: {1}'.format(eta, exc))
            self.eta = maybe_make_aware(eta, self.tzlocal)
        else:
            self.eta = None

        expires = headers.get('expires')
        if expires is not None:
            try:
                expires = maybe_iso8601(expires)
            except (AttributeError, ValueError, TypeError) as exc:
                raise InvalidTaskError(
                    'invalid expires value {0!r}: {1}'.format(expires, exc))
            self.expires = maybe_make_aware(expires, self.tzlocal)
        else:
            self.expires = None

        delivery_info = message.delivery_info or {}
        properties = message.properties or {}
        headers.update({
            'reply_to': properties.get('reply_to'),
            'correlation_id': properties.get('correlation_id'),
            'delivery_info': {
                'exchange': delivery_info.get('exchange'),
                'routing_key': delivery_info.get('routing_key'),
                'priority': properties.get('priority'),
                'redelivered': delivery_info.get('redelivered'),
            }

        })
        self.request_dict = headers