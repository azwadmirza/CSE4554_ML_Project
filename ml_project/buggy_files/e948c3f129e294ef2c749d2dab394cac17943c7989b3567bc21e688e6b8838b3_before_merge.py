    def destroy(self):
        if hasattr(self, 'stream') and self.stream is not None:
            # TODO: Optionally call stream.close() on newer pyzmq? It is broken on some.
            if self.stream.socket:
                self.stream.socket.close()
            self.stream.io_loop.remove_handler(self.stream.socket)
            # set this to None, more hacks for messed up pyzmq
            self.stream.socket = None
            self.stream = None
            self.socket.close()
        if self.context.closed is False:
            self.context.term()