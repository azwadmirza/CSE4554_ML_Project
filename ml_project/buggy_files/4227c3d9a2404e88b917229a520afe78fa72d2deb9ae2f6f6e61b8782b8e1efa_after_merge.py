    def portal_receive_server2portal(self, packed_data):
        """
        Receives message arriving to Portal from Server.
        This method is executed on the Portal.

        Args:
            packed_data (str): Pickled data (sessid, kwargs) coming over the wire.

        """
        try:
            sessid, kwargs = self.data_in(packed_data)
            session = self.factory.portal.sessions.get(sessid, None)
            if session:
                self.factory.portal.sessions.data_out(session, **kwargs)
        except Exception:
            logger.log_trace("packed_data len {}".format(len(packed_data)))
        return {}