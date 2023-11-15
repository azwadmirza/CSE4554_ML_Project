    def process(self):
        event = self.receive_message()

        try:
            self.output.lpush(self.queue, str(event))
        except Exception:
            self.logger.exception('Failed to send message. Reconnecting.')
            self.connect()
        else:
            self.acknowledge_message()