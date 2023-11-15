    def create_session(self):
        """Create OAuth session for user

        This configures the OAuth session based on the :py:class:`SocialToken`
        attributes. If there is an ``expires_at``, treat the session as an auto
        renewing token. Some providers expire tokens after as little as 2
        hours.
        """
        token = self.account.socialtoken_set.first()
        if token is None:
            return None

        token_config = {
            'access_token': token.token,
            'token_type': 'bearer',
        }
        if token.expires_at is not None:
            token_expires = (token.expires_at - datetime.now()).total_seconds()
            token_config.update({
                'refresh_token': token.token_secret,
                'expires_in': token_expires,
            })

        self.session = OAuth2Session(
            client_id=token.app.client_id,
            token=token_config,
            auto_refresh_kwargs={
                'client_id': token.app.client_id,
                'client_secret': token.app.secret,
            },
            auto_refresh_url=self.get_adapter().access_token_url,
            token_updater=self.token_updater(token)
        )

        return self.session or None