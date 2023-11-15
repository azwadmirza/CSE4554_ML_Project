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
        session = self.ssession()
        try:
            # Get second_id's values
            res = session.query(NickValues).filter(NickValues.nick_id == second_id).all()
            # Update first_id with second_id values if first_id doesn't have that key
            for row in res:
                first_res = session.query(NickValues) \
                    .filter(NickValues.nick_id == first_id) \
                    .filter(NickValues.key == row.key) \
                    .one_or_none()
                if not first_res:
                    self.set_nick_value(first_nick, row.key, _deserialize(row.value))
            session.query(NickValues).filter(NickValues.nick_id == second_id).delete()
            session.query(Nicknames) \
                .filter(Nicknames.nick_id == second_id) \
                .update({'nick_id': first_id})
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()