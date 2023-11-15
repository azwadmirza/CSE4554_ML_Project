    def send_message(self, *messages):
        for message in messages:
            if not message:
                self.logger.warning("Ignoring empty message at sending. Possible bug in bot.")
                continue
            if not self.__destination_pipeline:
                raise exceptions.ConfigurationError('pipeline', 'No destination pipeline given, '
                                                    'but needed')
                self.stop()

            self.logger.debug("Sending message.")
            self.__message_counter += 1
            if not self.__message_counter_start:
                self.__message_counter_start = datetime.datetime.now()
            if self.__message_counter % self.parameters.log_processed_messages_count == 0 or \
               datetime.datetime.now() - self.__message_counter_start > self.parameters.log_processed_messages_seconds:
                self.logger.info("Processed %d messages since last logging.", self.__message_counter)
                self.__message_counter = 0
                self.__message_counter_start = datetime.datetime.now()

            raw_message = libmessage.MessageFactory.serialize(message)
            self.__destination_pipeline.send(raw_message)