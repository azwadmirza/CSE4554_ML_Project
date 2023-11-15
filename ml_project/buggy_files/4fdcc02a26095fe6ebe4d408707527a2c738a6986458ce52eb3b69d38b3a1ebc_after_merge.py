    def recv_callback(self, fd, flags):
        if flags & (gobject.IO_ERR | gobject.IO_HUP):
            self.stop('Bad client flags: %s' % flags)
            return True

        try:
            data = self.sock.recv(4096)
        except socket.error as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EINTR):
                self.stop('Unexpected client error: %s' % e)
            return True

        if not data:
            self.disable_recv()
            self.actor_ref.tell({'close': True})
            return True

        try:
            self.actor_ref.tell({'received': data})
        except pykka.ActorDeadError:
            self.stop('Actor is dead.')

        return True