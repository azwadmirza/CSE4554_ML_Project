    def delete_nick_group(self, nick):
        """Removes a nickname, and all associated aliases and settings."""
        nick = Identifier(nick)
        nick_id = self.get_nick_id(nick, False)
        self.execute('DELETE FROM nicknames WHERE nick_id = ?', [nick_id])
        self.execute('DELETE FROM nick_values WHERE nick_id = ?', [nick_id])