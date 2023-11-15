    def login(self):
        result = dict(
            changed=False
        )

        if self.params['client_id'] is not None:
            try:
                self.conn = pysnow.OAuthClient(client_id=self.client_id,
                                               client_secret=self.client_secret,
                                               token_updater=self.updater,
                                               instance=self.instance)
            except Exception as detail:
                self.module.fail_json(msg='Could not connect to ServiceNow: {0}'.format(str(detail)), **result)
            if not self.session['token']:
                # No previous token exists, Generate new.
                try:
                    self.session['token'] = self.conn.generate_token(self.username, self.password)
                except pysnow.exceptions.TokenCreateError as detail:
                    self.module.fail_json(msg='Unable to generate a new token: {0}'.format(str(detail)), **result)

                self.conn.set_token(self.session['token'])
        elif self.username is not None:
            try:
                self.conn = pysnow.Client(instance=self.instance,
                                          user=self.username,
                                          password=self.password)
            except Exception as detail:
                self.module.fail_json(msg='Could not connect to ServiceNow: {0}'.format(str(detail)), **result)
        else:
            snow_error = "Must specify username/password. Also client_id/client_secret if using OAuth."
            self.module.fail_json(msg=snow_error, **result)