    def authenticate(self):
        if self.m.is_authenticated():
            return
        # Checks for OAuth2 credentials,
        # if they don't exist - performs authorization
        oauth_file = self.config['oauth_file'].as_filename()
        if os.path.isfile(oauth_file):
            uploader_id = self.config['uploader_id']
            uploader_name = self.config['uploader_name']
            self.m.login(oauth_credentials=oauth_file,
                         uploader_id=uploader_id.as_str().upper() or None,
                         uploader_name=uploader_name.as_str() or None)
        else:
            self.m.perform_oauth(oauth_file)