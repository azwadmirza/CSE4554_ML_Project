    def get_channel_value(self, channel, key):
        """Retrieves the value for a given key associated with a channel."""
        channel = Identifier(channel).lower()
        result = self.execute(
            'SELECT value FROM channel_values WHERE channel = ? AND key = ?',
            [channel, key]
        ).fetchone()
        if result is not None:
            result = result[0]
        return _deserialize(result)