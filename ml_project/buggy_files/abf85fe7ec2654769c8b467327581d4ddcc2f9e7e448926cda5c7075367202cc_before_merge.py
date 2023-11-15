    def merge_nick_groups(self, first_nick, second_nick):
        """Merges the nick groups for the specified nicks.

        Takes two nicks, which may or may not be registered.  Unregistered
        nicks will be registered. Keys which are set for only one of the given
        nicks will be preserved. Where multiple nicks have values for a given
        key, the value set for the first nick will be used.

        Note that merging of data only applies to the native key-value store.
        If modules define their own tables which rely on the nick table, they
        will need to have their merging done separately."""
        first_id = self.get_nick_id(Identifier(first_nick))
        second_id = self.get_nick_id(Identifier(second_nick))
        self.execute(
            'UPDATE OR IGNORE nick_values SET nick_id = ? WHERE nick_id = ?',
            [first_id, second_id])
        self.execute('DELETE FROM nick_values WHERE nick_id = ?', [second_id])
        self.execute('UPDATE nicknames SET nick_id = ? WHERE nick_id = ?',
                     [first_id, second_id])