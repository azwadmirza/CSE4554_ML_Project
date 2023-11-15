    def send_pack(self, message, binary=False):
        if IOLoop.current(False) == self.server.io_loop:
            # Running in Main Thread
            # Send message
            try:
                self.write_message(message, binary).add_done_callback(self.send_complete)
            except (IOError, WebSocketError):
                self.server.io_loop.add_callback(self.on_close)
        else:
            # Not running in Main Thread so use proper thread to send message
            self.server.io_loop.add_callback(lambda: self.send_pack(message, binary))