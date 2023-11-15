    def send(self, body, title='', notify_type=NotifyType.INFO, **kwargs):
        """
        Perform XMPP Notification
        """

        if not self._enabled:
            self.logger.warning(
                'XMPP Notifications are not supported by this system '
                '- install sleekxmpp.')
            return False

        # Detect our JID if it isn't otherwise specified
        jid = self.jid
        password = self.password
        if not jid:
            if self.user and self.password:
                # xmpp://user:password@hostname
                jid = '{}@{}'.format(self.user, self.host)

            else:
                # xmpp://password@hostname
                jid = self.host
                password = self.password if self.password else self.user

        # Compute port number
        if not self.port:
            port = self.default_secure_port \
                if self.secure else self.default_unsecure_port

        else:
            port = self.port

        try:
            # Communicate with XMPP.
            xmpp_adapter = SleekXmppAdapter(
                host=self.host, port=port, secure=self.secure,
                verify_certificate=self.verify_certificate, xep=self.xep,
                jid=jid, password=password, body=body, targets=self.targets,
                before_message=self.throttle, logger=self.logger)

        except ValueError:
            # We failed
            return False

        # Initialize XMPP machinery and begin processing the XML stream.
        outcome = xmpp_adapter.process()

        return outcome