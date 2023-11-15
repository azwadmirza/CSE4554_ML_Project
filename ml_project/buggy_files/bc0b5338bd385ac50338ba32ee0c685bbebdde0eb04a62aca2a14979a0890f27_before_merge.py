    def unalias_nick(self, alias):
        """Removes an alias.

        Raises ValueError if there is not at least one other nick in the group.
        To delete an entire group, use `delete_group`.
        """
        alias = Identifier(alias)
        nick_id = self.get_nick_id(alias, False)
        count = self.execute('SELECT COUNT(*) FROM nicknames WHERE nick_id = ?',
                             [nick_id]).fetchone()[0]
        if count <= 1:
            raise ValueError('Given alias is the only entry in its group.')
        self.execute('DELETE FROM nicknames WHERE slug = ?', [alias.lower()])