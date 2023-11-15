    def delete_nick_group(self, nick):
        """Removes a nickname, and all associated aliases and settings."""
        nick = Identifier(nick)
        nick_id = self.get_nick_id(nick, False)
        session = self.ssession()
        try:
            session.query(Nicknames).filter(Nicknames.nick_id == nick_id).delete()
            session.query(NickValues).filter(NickValues.nick_id == nick_id).delete()
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()