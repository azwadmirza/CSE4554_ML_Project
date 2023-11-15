    def _async_open(self, session_id, proto_version):
        ''' Perform the specific steps needed to open a connection to a Bokeh session

        Sepcifically, this method coordinates:

        * Getting a session for a session ID (creating a new one if needed)
        * Creating a protocol receiver and hander
        * Opening a new ServerConnection and sending it an ACK

        Args:
            session_id (str) :
                A session ID to for a session to connect to

                If no session exists with the given ID, a new session is made

            proto_version (str):
                The protocol version requested by the connecting client.

        Returns:
            None

        '''
        try:
            yield self.application_context.create_session_if_needed(session_id, self.request)
            session = self.application_context.get_session(session_id)

            protocol = Protocol(proto_version)
            self.receiver = Receiver(protocol)
            log.debug("Receiver created for %r", protocol)

            self.handler = ProtocolHandler()
            log.debug("ProtocolHandler created for %r", protocol)

            self.connection = self.application.new_connection(protocol, self, self.application_context, session)
            log.info("ServerConnection created")

        except ProtocolError as e:
            log.error("Could not create new server session, reason: %s", e)
            self.close()
            raise e

        msg = self.connection.protocol.create('ACK')
        yield self.send_message(msg)

        raise gen.Return(None)