    def get_exit_status(self, channel):
        """Get exit status from channel if ready else return `None`.

        :rtype: int or `None`
        """
        if not channel.is_eof():
            return
        return channel.get_exit_status()