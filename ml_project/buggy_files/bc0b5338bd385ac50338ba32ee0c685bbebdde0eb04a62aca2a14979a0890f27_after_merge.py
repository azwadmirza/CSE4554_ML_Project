    def unalias_nick(self, alias):
        """Removes an alias.

        Raises ValueError if there is not at least one other nick in the group.
        To delete an entire group, use `delete_group`.
        """
        alias = Identifier(alias)
        nick_id = self.get_nick_id(alias, False)
        session = self.ssession()
        try:
            count = session.query(Nicknames) \
                .filter(Nicknames.nick_id == nick_id) \
                .count()
            if count <= 1:
                raise ValueError('Given alias is the only entry in its group.')
            session.query(Nicknames).filter(Nicknames.slug == alias.lower()).delete()
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()