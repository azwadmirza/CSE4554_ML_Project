    def alias_nick(self, nick, alias):
        """Create an alias for a nick.

        Raises ValueError if the alias already exists. If nick does not already
        exist, it will be added along with the alias."""
        nick = Identifier(nick)
        alias = Identifier(alias)
        nick_id = self.get_nick_id(nick)
        session = self.ssession()
        try:
            result = session.query(Nicknames) \
                .filter(Nicknames.slug == alias.lower()) \
                .filter(Nicknames.canonical == alias) \
                .one_or_none()
            if result:
                raise ValueError('Given alias is the only entry in its group.')
            nickname = Nicknames(nick_id=nick_id, slug=alias.lower(), canonical=alias)
            session.add(nickname)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()