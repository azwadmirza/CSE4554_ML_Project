    def store_user(self, data):
        # mocks a ConnectionState for appropriate use for Message
        return BaseUser(state=self.webhook._state, data=data)