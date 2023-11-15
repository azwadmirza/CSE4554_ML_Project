    def kill(self, master):
        """
            Kill this request.
        """
        from ..protocol import Kill

        self.error = Error("Connection killed")
        self.intercepted = False
        self.reply(Kill)
        master.handle_error(self)