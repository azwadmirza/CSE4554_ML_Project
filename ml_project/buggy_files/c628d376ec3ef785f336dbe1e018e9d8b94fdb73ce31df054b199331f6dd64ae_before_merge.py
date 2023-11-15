    def get_nick_id(self, nick, create=True):
        """Return the internal identifier for a given nick.

        This identifier is unique to a user, and shared across all of that
        user's aliases. If create is True, a new ID will be created if one does
        not already exist"""
        slug = nick.lower()
        nick_id = self.execute('SELECT nick_id from nicknames where slug = ?',
                               [slug]).fetchone()
        if nick_id is None:
            if not create:
                raise ValueError('No ID exists for the given nick')
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO nick_ids VALUES (NULL)')
                nick_id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
                cur.execute(
                    'INSERT INTO nicknames (nick_id, slug, canonical) VALUES '
                    '(?, ?, ?)',
                    [nick_id, slug, nick]
                )
            nick_id = self.execute('SELECT nick_id from nicknames where slug = ?',
                                   [slug]).fetchone()
        return nick_id[0]