    def process_message(self, message):
        message_type, payload = decode_msg(message)
        if message_type in self.ordered_messages:
            chan_id = payload.get('channel_id') or payload["temporary_channel_id"]
            self.ordered_message_queues[chan_id].put_nowait((message_type, payload))
        else:
            if message_type != 'error' and 'channel_id' in payload:
                chan = self.get_channel_by_id(payload['channel_id'])
                if chan is None:
                    raise Exception('Got unknown '+ message_type)
                args = (chan, payload)
            else:
                args = (payload,)
            try:
                f = getattr(self, 'on_' + message_type)
            except AttributeError:
                #self.logger.info("Received '%s'" % message_type.upper(), payload)
                return
            # raw message is needed to check signature
            if message_type in ['node_announcement', 'channel_announcement', 'channel_update']:
                payload['raw'] = message
            execution_result = f(*args)
            if asyncio.iscoroutinefunction(f):
                asyncio.ensure_future(execution_result)