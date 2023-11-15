    def save_token(self, access_token):
        """
        Stores an access token in the database.

        :param access_token: An instance of :class:`oauth2.datatype.AccessToken`.

        """
        
        user = self.db.query(orm.User).filter(orm.User.id == access_token.user_id).first()
        orm_access_token = orm.OAuthAccessToken(
            client_id=access_token.client_id,
            grant_type=access_token.grant_type,
            expires_at=access_token.expires_at,
            refresh_token=access_token.refresh_token,
            refresh_expires_at=access_token.refresh_expires_at,
            token=access_token.token,
            user=user,
        )
        self.db.add(orm_access_token)
        self.db.commit()