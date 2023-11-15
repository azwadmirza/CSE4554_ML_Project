    def set_nick_value(self, nick, key, value):
        """Sets the value for a given key to be associated with the nick."""
        nick = Identifier(nick)
        value = json.dumps(value, ensure_ascii=False)
        nick_id = self.get_nick_id(nick)
        self.execute('INSERT OR REPLACE INTO nick_values VALUES (?, ?, ?)',
                     [nick_id, key, value])