    def as_task_v2(self, task_id, name, args=None, kwargs=None,
                   countdown=None, eta=None, group_id=None,
                   expires=None, retries=0, chord=None,
                   callbacks=None, errbacks=None, reply_to=None,
                   time_limit=None, soft_time_limit=None,
                   create_sent_event=False, root_id=None, parent_id=None,
                   shadow=None, chain=None, now=None, timezone=None,
                   origin=None, argsrepr=None, kwargsrepr=None):
        args = args or ()
        kwargs = kwargs or {}
        if not isinstance(args, (list, tuple)):
            raise TypeError('task args must be a list or tuple')
        if not isinstance(kwargs, Mapping):
            raise TypeError('task keyword arguments must be a mapping')
        if countdown:  # convert countdown to ETA
            self._verify_seconds(countdown, 'countdown')
            now = now or self.app.now()
            timezone = timezone or self.app.timezone
            eta = maybe_make_aware(
                now + timedelta(seconds=countdown), tz=timezone,
            )
        if isinstance(expires, numbers.Real):
            self._verify_seconds(expires, 'expires')
            now = now or self.app.now()
            timezone = timezone or self.app.timezone
            expires = maybe_make_aware(
                now + timedelta(seconds=expires), tz=timezone,
            )
        if not isinstance(eta, string_t):
            eta = eta and eta.isoformat()
        # If we retry a task `expires` will already be ISO8601-formatted.
        if not isinstance(expires, string_t):
            expires = expires and expires.isoformat()

        if argsrepr is None:
            argsrepr = saferepr(args, self.argsrepr_maxsize)
        if kwargsrepr is None:
            kwargsrepr = saferepr(kwargs, self.kwargsrepr_maxsize)

        if JSON_NEEDS_UNICODE_KEYS:  # pragma: no cover
            if callbacks:
                callbacks = [utf8dict(callback) for callback in callbacks]
            if errbacks:
                errbacks = [utf8dict(errback) for errback in errbacks]
            if chord:
                chord = utf8dict(chord)

        if not root_id:  # empty root_id defaults to task_id
            root_id = task_id

        return task_message(
            headers={
                'lang': 'py',
                'task': name,
                'id': task_id,
                'shadow': shadow,
                'eta': eta,
                'expires': expires,
                'group': group_id,
                'retries': retries,
                'timelimit': [time_limit, soft_time_limit],
                'root_id': root_id,
                'parent_id': parent_id,
                'argsrepr': argsrepr,
                'kwargsrepr': kwargsrepr,
                'origin': origin or anon_nodename()
            },
            properties={
                'correlation_id': task_id,
                'reply_to': reply_to or '',
            },
            body=(
                args, kwargs, {
                    'callbacks': callbacks,
                    'errbacks': errbacks,
                    'chain': chain,
                    'chord': chord,
                },
            ),
            sent_event={
                'uuid': task_id,
                'root_id': root_id,
                'parent_id': parent_id,
                'name': name,
                'args': argsrepr,
                'kwargs': kwargsrepr,
                'retries': retries,
                'eta': eta,
                'expires': expires,
            } if create_sent_event else None,
        )