    def handle(self, message):
        '''
        Dispatches a message based on the message type to a handler function
        of name onX where X is the message type.
        '''
        topology_id = message.get('topology')
        assert topology_id is not None, "No topology_id"
        client_id = message.get('client')
        assert client_id is not None, "No client_id"
        message_type, message_value = self.parse_message_text(message['text'], client_id)
        if message_type is None:
            return
        handler = self.get_handler(message_type)
        if handler is not None:
            handler(message_value, topology_id, client_id)
        else:
            logger.warning("Unsupported message %s: no handler", message_type)