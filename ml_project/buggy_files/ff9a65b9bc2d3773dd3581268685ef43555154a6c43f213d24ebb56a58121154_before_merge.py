    def preferences(self):
        user = self.trans.user
        return user and user.extra_preferences