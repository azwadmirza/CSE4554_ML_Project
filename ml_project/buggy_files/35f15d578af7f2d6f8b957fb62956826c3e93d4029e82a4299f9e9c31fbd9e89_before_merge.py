    def receive_message(self):
        if self.__current_message:
            self.logger.debug("Reusing existing current message as incoming.")
            return self.__current_message

        self.logger.debug('Waiting for incoming message.')
        message = None
        while not message:
            message = self.__source_pipeline.receive()
            if not message:
                self.logger.warning('Empty message received. Some previous bot sent invalid data.')
                continue

        # handle a sighup which happened during blocking read
        self.__handle_sighup()

        try:
            self.__current_message = libmessage.MessageFactory.unserialize(message,
                                                                           harmonization=self.harmonization)
        except exceptions.InvalidKey as exc:
            # In case a incoming message is malformed an does not conform with the currently
            # loaded harmonization, stop now as this will happen repeatedly without any change
            raise exceptions.ConfigurationError('harmonization', exc.args[0])

        if self.logger.isEnabledFor(logging.DEBUG):
            if 'raw' in self.__current_message and len(self.__current_message['raw']) > 400:
                tmp_msg = self.__current_message.to_dict(hierarchical=False)
                tmp_msg['raw'] = tmp_msg['raw'][:397] + '...'
            else:
                tmp_msg = self.__current_message
            self.logger.debug('Received message %r.', tmp_msg)

        return self.__current_message