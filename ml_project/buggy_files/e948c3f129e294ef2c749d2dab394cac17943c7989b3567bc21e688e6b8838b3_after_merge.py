    def destroy(self):
        if hasattr(self, 'stream') and self.stream is not None:
            self.stream.close()
            self.socket = None
            self.stream = None
        if self.context.closed is False:
            self.context.term()