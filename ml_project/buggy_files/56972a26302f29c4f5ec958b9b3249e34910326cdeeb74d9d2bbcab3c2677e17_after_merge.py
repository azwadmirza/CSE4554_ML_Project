    def send(self, frame, flags=0, copy=True, track=False):
        '''Send a single frame while enforcing VIP protocol.

        Expects frames to be sent in the following order:

           PEER USER_ID MESSAGE_ID SUBSYSTEM [ARG]...

        If the socket is a ROUTER, an INTERMEDIARY must be sent before
        PEER. The VIP protocol signature, PROTO, is automatically sent
        between PEER and USER_ID. Zero or more ARG frames may be sent
        after SUBSYSTEM, which may not be empty. All frames up to
        SUBSYSTEM must be sent with the SNDMORE flag.
        '''
        self.wait_send(flags)
        state = self._send_state
        if state == 4:
            # Verify that subsystem has some non-space content
            subsystem = bytes(frame)
            if not subsystem.strip():
                raise ProtocolError('invalid subsystem: {!r}'.format(subsystem))
        if not flags & SNDMORE:
            # Must have SNDMORE flag until sending SUBSYSTEM frame.
            if state < 4:
                raise ProtocolError(
                    'expecting at least {} more frames'.format(4 - state - 1))
            # Reset the send state when the last frame is sent
            self._send_state = -1 if self.type == ROUTER else 0
        elif state < 5:
            if state == 1:
                # Automatically send PROTO frame
                super(_Socket, self).send(b'VIP1', flags=flags|SNDMORE)
                state += 1
            self._send_state = state + 1
        try:
            super(_Socket, self).send(
                frame, flags=flags, copy=copy, track=track)
        except Exception:
            self._send_state = state
            raise