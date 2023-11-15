    def get_private_user_role(self, user, auto_create=False):
        role = self.sa_session.query(self.model.Role) \
                              .filter(and_(self.model.UserRoleAssociation.table.c.user_id == user.id,
                                           self.model.Role.table.c.id == self.model.UserRoleAssociation.table.c.role_id,
                                           self.model.Role.table.c.type == self.model.Role.types.PRIVATE)) \
                              .first()
        if not role:
            if auto_create:
                return self.create_private_user_role(user)
            else:
                return None
        return role