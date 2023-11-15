    def parse_message_text(self, message_text, client_id):
        '''
        See the Messages of CONTRIBUTING.md for the message format.
        '''
        data = json.loads(message_text)
        if len(data) == 2:
            message_type = data.pop(0)
            message_value = data.pop(0)
            if isinstance(message_value, list):
                logger.error("Message has no sender")
                return None, None
            if isinstance(message_value, dict) and client_id != message_value.get('sender'):
                logger.error("client_id mismatch expected: %s actual %s", client_id, message_value.get('sender'))
                return None, None
            return message_type, message_value
        else:
            logger.error("Invalid message text")
            return None, None