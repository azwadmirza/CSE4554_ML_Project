    def get_nick_value(self, nick, key):
        """Retrieves the value for a given key associated with a nick."""
        nick = Identifier(nick)
        result = self.execute(
            'SELECT value FROM nicknames JOIN nick_values '
            'ON nicknames.nick_id = nick_values.nick_id '
            'WHERE slug = ? AND key = ?',
            [nick.lower(), key]
        ).fetchone()
        if result is not None:
            result = result[0]
        return _deserialize(result)