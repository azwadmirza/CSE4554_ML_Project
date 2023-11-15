    def send_message(self, message):
        ''' Send a Bokeh Server protocol message to the connected client.

        Args:
            message (Message) : a message to send

        '''
        try:
            yield message.send(self)
        except (WebSocketClosedError, StreamClosedError): # Tornado 4.x may raise StreamClosedError
            # on_close() is / will be called anyway
            log.warn("Failed sending message as connection was closed")
        raise gen.Return(None)