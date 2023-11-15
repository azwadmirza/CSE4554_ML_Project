    async def get(self):
        user = self.current_user
        if user is None:
            # whoami can be accessed via oauth token
            user = self.get_current_user_oauth_token()
        if user is None:
            raise web.HTTPError(403)
        if isinstance(user, orm.Service):
            model = self.service_model(user)
        else:
            model = self.user_model(user)
        self.write(json.dumps(model))