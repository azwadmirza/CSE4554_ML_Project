    def open_session(self):
        """Open new channel from session"""
        try:
            chan = self._eagain(self.session.open_session)
        except Exception as ex:
            raise SessionError(ex)
        # Multiple forward requests result in ChannelRequestDenied
        # errors, flag is used to avoid this.
        if self.forward_ssh_agent and not self._forward_requested:
            if not hasattr(chan, 'request_auth_agent'):
                warn("Requested SSH Agent forwarding but libssh2 version used "
                     "does not support it - ignoring")
                return chan
            self._eagain(chan.request_auth_agent)
            self._forward_requested = True
        return chan