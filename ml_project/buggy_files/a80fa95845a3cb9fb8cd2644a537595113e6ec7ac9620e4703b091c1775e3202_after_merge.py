    def on_message(self, prepare, message):
        _type = message.delivery_info['routing_key']

        # For redis when `fanout_patterns=False` (See Issue #1882)
        if _type.split('.', 1)[0] == 'task':
            return
        try:
            handler = self.event_handlers[_type]
        except KeyError:
            pass
        else:
            return handler(message.payload)

        # proto2: hostname in header; proto1: in body
        hostname = (message.headers.get('hostname') or
                    message.payload['hostname'])
        if hostname != self.hostname:
            try:
                _, event = prepare(message.payload)
                self.update_state(event)
            except (DecodeError, ContentDisallowed, TypeError) as exc:
                logger.error(exc)
        else:
            self.clock.forward()