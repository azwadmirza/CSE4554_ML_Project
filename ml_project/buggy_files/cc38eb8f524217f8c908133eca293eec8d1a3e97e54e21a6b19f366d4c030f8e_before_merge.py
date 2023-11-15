    def get_user_data(self):
        user_data = self.module.params.get('user_data')
        if user_data is not None:
            user_data = base64.b64encode(str(user_data))
        return user_data