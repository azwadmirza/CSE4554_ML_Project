    def create_task_handler(self, promise=promise):
        strategies = self.strategies
        on_unknown_message = self.on_unknown_message
        on_unknown_task = self.on_unknown_task
        on_invalid_task = self.on_invalid_task
        callbacks = self.on_task_message
        call_soon = self.call_soon

        def on_task_received(message):
            # payload will only be set for v1 protocol, since v2
            # will defer deserializing the message body to the pool.
            payload = None
            try:
                type_ = message.headers['task']                # protocol v2
            except TypeError:
                return on_unknown_message(None, message)
            except KeyError:
                try:
                    payload = message.decode()
                except Exception as exc:  # pylint: disable=broad-except
                    return self.on_decode_error(message, exc)
                try:
                    type_, payload = payload['task'], payload  # protocol v1
                except (TypeError, KeyError):
                    return on_unknown_message(payload, message)
            try:
                strategy = strategies[type_]
            except KeyError as exc:
                return on_unknown_task(None, message, exc)
            else:
                try:
                    strategy(
                        message, payload,
                        promise(call_soon, (message.ack_log_error,)),
                        promise(call_soon, (message.reject_log_error,)),
                        callbacks,
                    )
                except InvalidTaskError as exc:
                    return on_invalid_task(payload, message, exc)
                except DecodeError as exc:
                    return self.on_decode_error(message, exc)

        return on_task_received