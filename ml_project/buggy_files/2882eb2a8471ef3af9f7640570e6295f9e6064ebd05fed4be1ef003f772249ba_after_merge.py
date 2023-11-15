    def destroy(self):
        if hasattr(self, 'stream'):
            # TODO: Optionally call stream.close() on newer pyzmq? It is broken on some.
            self.stream.socket.close()
            self.stream.io_loop.remove_handler(self.stream.socket)
            # set this to None, more hacks for messed up pyzmq
            self.stream.socket = None
            self.socket.close()
        self.context.term()