    def handle(self, message):
        '''
        Dispatches a message based on the message type to a handler function
        of name onX where X is the message type.
        '''
        topology_id = message.get('topology')
        if topology_id is None:
            logger.warning("Unsupported message %s: no topology", message)
            return
        client_id = message.get('client')
        if client_id is None:
            logger.warning("Unsupported message %s: no client", message)
            return
        if 'text' not in message:
            logger.warning("Unsupported message %s: no data", message)
            return
        message_type, message_value = self.parse_message_text(message['text'], client_id)
        if message_type is None:
            logger.warning("Unsupported message %s: no message type", message)
            return
        handler = self.get_handler(message_type)
        if handler is not None:
            handler(message_value, topology_id, client_id)
        else:
            logger.warning("Unsupported message %s: no handler", message_type)