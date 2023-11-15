    def send_vip(self, peer, subsystem, args=None, msg_id=b'',
                 user=b'', via=None, flags=0, copy=True, track=False):
        '''Send an entire VIP message by individual parts.

        This method will raise a ProtocolError exception if the previous
        send was made with the SNDMORE flag or if other protocol
        constraints are violated. If SNDMORE flag is used, additional
        arguments may be sent. via is required for ROUTER sockets.
        '''
        state = self._send_state
        if state > 0:
            raise ProtocolError('previous send operation is not complete')
        elif state == -1:
            if via is None:
                raise ValueError("missing 'via' argument "
                                 "required by ROUTER sockets")
            self.send(via, flags=flags|SNDMORE, copy=copy, track=track)
        if msg_id is None:
            msg_id = b''
        if user is None:
            user = b''
        more = SNDMORE if args else 0
        self.send_multipart([peer, user, msg_id, subsystem],
                            flags=flags|more, copy=copy, track=track)
        if args:
            send = (self.send if isinstance(args, basestring)
                    else self.send_multipart)
            send(args, flags=flags, copy=copy, track=track)