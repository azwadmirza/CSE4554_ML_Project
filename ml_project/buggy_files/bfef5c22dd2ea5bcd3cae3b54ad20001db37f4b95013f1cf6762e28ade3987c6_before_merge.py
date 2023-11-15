    def process(self):
        ''' Stop the Bot if cannot connect to AMQP Server after the defined connection attempts '''

        # self.connection and self.channel can be None
        if getattr(self.connection, 'is_closed', None) or getattr(self.channel, 'is_closed', None):
                self.connect_server()

        event = self.receive_message()

        if not self.keep_raw_field:
            del event['raw']

        try:
            if not self.channel.basic_publish(exchange=self.exchange,
                                              routing_key=self.routing_key,
                                              body=event.to_json(),
                                              properties=self.properties,
                                              mandatory=True):
                if self.require_confirmation:
                    raise ValueError('Message sent but not confirmed.')
                else:
                    self.logger.info('Message sent but not confirmed.')
        except (pika.exceptions.ChannelError, pika.exceptions.AMQPChannelError,
                pika.exceptions.NackError):
            self.logger.exception('Error publishing the message.')
        else:
            self.acknowledge_message()