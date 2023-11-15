    def get_exit_status(self, channel):
        if not channel.eof():
            return
        return channel.get_exit_status()